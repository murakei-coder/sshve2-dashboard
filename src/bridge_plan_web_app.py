"""
Bridge Plan Generator - Web Application
営業担当が簡単に使えるWebインターフェース
"""

from flask import Flask, render_template, request, jsonify, send_file
import sys
from pathlib import Path
import pandas as pd
import json
from datetime import datetime
import traceback

# Add src directory to path for imports
src_path = Path(__file__).parent
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

import bridge_config
from bridge_plan_generator import data_loader
from bridge_plan_generator import sourcing_processor
from bridge_plan_generator import target_processor
from bridge_plan_generator import suppression_processor
from bridge_plan_generator import hierarchy_processor
from bridge_plan_generator import promotion_ops_calculator
from bridge_plan_generator import sourcing_plan_generator
from bridge_plan_generator import suppression_plan_generator
from bridge_plan_generator import bridge_plan_orchestrator
from bridge_plan_generator import report_generator

app = Flask(__name__, template_folder='../templates')

# Global variables to cache loaded data
cached_data = {
    'config': None,
    'sourcing_df': None,
    'target_df': None,
    'benchmark_df': None,
    'mapping_df': None,
    'hierarchy_map': None,
    'last_loaded': None
}


def load_data():
    """Load all data files and cache them."""
    try:
        # Load configuration
        config = bridge_config.Config.load_from_file('config/bridge_config.json')
        
        # Validate configuration
        is_valid, error_msg = config.validate()
        if not is_valid:
            return False, f"設定ファイルエラー: {error_msg}"
        
        # Initialize components
        data_loader_obj = data_loader.DataLoader()
        sourcing_processor_obj = sourcing_processor.SourcingProcessor()
        hierarchy_processor_obj = hierarchy_processor.HierarchyProcessor()
        
        # Load data files
        sourcing_df = data_loader_obj.load_sourcing_data(config.sourcing_data_path)
        target_df = data_loader_obj.load_target_data(config.target_data_path)
        benchmark_df = data_loader_obj.load_suppression_benchmark(config.suppression_benchmark_path)
        mapping_df = data_loader_obj.load_cid_mapping(config.cid_mapping_path, config.cid_mapping_sheet)
        
        # Build hierarchy map
        hierarchy_map = hierarchy_processor_obj.build_hierarchy_map(mapping_df)
        
        # Cache data
        cached_data['config'] = config
        cached_data['sourcing_df'] = sourcing_df
        cached_data['target_df'] = target_df
        cached_data['benchmark_df'] = benchmark_df
        cached_data['mapping_df'] = mapping_df
        cached_data['hierarchy_map'] = hierarchy_map
        cached_data['last_loaded'] = datetime.now()
        
        return True, "データ読み込み成功"
    
    except Exception as e:
        return False, f"データ読み込みエラー: {str(e)}"


@app.route('/')
def index():
    """Main page."""
    return render_template('bridge_plan_app.html')


@app.route('/api/load_data', methods=['POST'])
def api_load_data():
    """API endpoint to load data."""
    success, message = load_data()
    
    if success:
        # Get entity counts
        config = cached_data['config']
        mapping_df = cached_data['mapping_df']
        
        stats = {
            'cid_count': len(mapping_df['CID'].unique()),
            'alias_count': len(mapping_df['Alias'].unique()),
            'mgr_count': len(mapping_df['Mgr'].unique()),
            'team_count': len(mapping_df['Team'].unique()),
            'last_loaded': cached_data['last_loaded'].strftime('%Y-%m-%d %H:%M:%S')
        }
        
        return jsonify({'success': True, 'message': message, 'stats': stats})
    else:
        return jsonify({'success': False, 'message': message})


@app.route('/api/get_entities', methods=['POST'])
def api_get_entities():
    """Get list of entities for selected level."""
    data = request.json
    level = data.get('level')
    
    if not cached_data['mapping_df'] is not None:
        return jsonify({'success': False, 'message': 'データが読み込まれていません'})
    
    try:
        mapping_df = cached_data['mapping_df']
        entities = sorted(mapping_df[level].unique().tolist())
        
        return jsonify({'success': True, 'entities': entities})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})


@app.route('/api/generate_plan', methods=['POST'])
def api_generate_plan():
    """Generate bridge plan."""
    data = request.json
    level = data.get('level')
    entity_id = data.get('entity_id', None)
    
    if cached_data['config'] is None:
        return jsonify({'success': False, 'message': 'データが読み込まれていません'})
    
    try:
        config = cached_data['config']
        sourcing_df = cached_data['sourcing_df']
        target_df = cached_data['target_df']
        benchmark_df = cached_data['benchmark_df']
        mapping_df = cached_data['mapping_df']
        hierarchy_map = cached_data['hierarchy_map']
        
        # Initialize processors
        sourcing_processor_obj = sourcing_processor.SourcingProcessor()
        target_processor_obj = target_processor.TargetProcessor()
        suppression_processor_obj = suppression_processor.SuppressionProcessor()
        hierarchy_processor_obj = hierarchy_processor.HierarchyProcessor()
        
        # Process data
        t30_gms_df = sourcing_processor_obj.extract_t30_gms_bau(sourcing_df)
        cid_aggregated = sourcing_processor_obj.aggregate_by_cid(t30_gms_df)
        targets_df = target_processor_obj.extract_targets(target_df)
        gaps_df = target_processor_obj.calculate_gaps(cid_aggregated, targets_df)
        
        # Extract suppression data
        benchmark_percentages = suppression_processor_obj.extract_benchmark_percentages(benchmark_df)
        current_suppression_df = suppression_processor_obj.calculate_current_suppression(sourcing_df)
        
        current_suppression_dict = {}
        for _, row in current_suppression_df.iterrows():
            current_suppression_dict[row['suppression_category_name']] = row['percentage']
        
        # Aggregate to requested level
        if level == 'CID':
            aggregated_df = gaps_df
        elif level == 'Alias':
            aggregated_df = hierarchy_processor_obj.aggregate_by_alias(gaps_df, hierarchy_map)
        elif level == 'Mgr':
            aggregated_df = hierarchy_processor_obj.aggregate_by_manager(gaps_df, hierarchy_map)
        elif level == 'Team':
            aggregated_df = hierarchy_processor_obj.aggregate_by_team(gaps_df, hierarchy_map)
        
        # Filter to specific entity if requested
        if entity_id:
            aggregated_df = aggregated_df[aggregated_df[level] == entity_id]
            if aggregated_df.empty:
                return jsonify({'success': False, 'message': f'エンティティ "{entity_id}" が見つかりません'})
        
        # Initialize plan generators
        promotion_ops_calc = promotion_ops_calculator.PromotionOPSCalculator(config.suppression_coefficients)
        sourcing_generator = sourcing_plan_generator.SourcingPlanGenerator()
        suppression_generator = suppression_plan_generator.SuppressionPlanGenerator(config.suppression_coefficients)
        orchestrator = bridge_plan_orchestrator.BridgePlanOrchestrator(sourcing_generator, suppression_generator)
        report_generator_obj = report_generator.ReportGenerator()
        
        # Generate bridge plans
        all_plans = []
        
        for idx, row in aggregated_df.iterrows():
            entity_id_str = str(row[level])
            current_t30_gms = row.get('t30_gms_bau_total', 0)
            target_t30_gms = row.get('t30_gms_target', 0)
            gap = row.get('gap', 0)
            
            # Get sourcing data for this entity
            if level == 'CID':
                entity_sourcing = sourcing_df[sourcing_df['CID'] == entity_id_str].copy()
            else:
                # Get all CIDs for this entity
                if level == 'Alias':
                    entity_cids = [cid for cid, alias in hierarchy_map.cid_to_alias.items() if alias == entity_id_str]
                elif level == 'Mgr':
                    entity_aliases = [alias for alias, mgr in hierarchy_map.alias_to_manager.items() if mgr == entity_id_str]
                    entity_cids = [cid for cid, alias in hierarchy_map.cid_to_alias.items() if alias in entity_aliases]
                elif level == 'Team':
                    entity_mgrs = [mgr for mgr, team in hierarchy_map.manager_to_team.items() if team == entity_id_str]
                    entity_aliases = [alias for alias, mgr in hierarchy_map.alias_to_manager.items() if mgr in entity_mgrs]
                    entity_cids = [cid for cid, alias in hierarchy_map.cid_to_alias.items() if alias in entity_aliases]
                
                entity_sourcing = sourcing_df[sourcing_df['CID'].isin(entity_cids)].copy()
            
            # Add participation scores
            entity_sourcing['participation_score'] = entity_sourcing.apply(
                lambda row: sourcing_processor_obj.calculate_participation_score({
                    flag: row[flag] for flag in config.event_flag_priority
                }),
                axis=1
            )
            
            entity_sourcing['t30_gms_bau'] = entity_sourcing['total_t30d_gms_BAU']
            
            # Generate all patterns
            patterns = orchestrator.generate_all_patterns(
                entity_id=entity_id_str,
                aggregation_level=level,
                current_t30_gms=current_t30_gms,
                target_t30_gms=target_t30_gms,
                gap=gap,
                sourcing_data=entity_sourcing,
                current_suppression=current_suppression_dict,
                benchmark_suppression=benchmark_percentages
            )
            
            all_plans.extend(patterns)
        
        # Export reports
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_dir = Path('output')
        output_dir.mkdir(parents=True, exist_ok=True)
        
        summary_csv = output_dir / f"bridge_plan_summary_{level}_{timestamp}.csv"
        excel_file = output_dir / f"bridge_plan_detailed_{level}_{timestamp}.xlsx"
        
        report_generator_obj.export_to_csv(all_plans, str(summary_csv))
        report_generator_obj.export_to_excel(all_plans, str(excel_file))
        
        # Prepare summary for display
        summary = []
        for plan in all_plans:
            # Calculate contributions
            sourcing_contribution = plan.sourcing_plan.gap_closable_by_sourcing if plan.sourcing_plan else 0
            suppression_contribution = plan.suppression_plan.gap_closable_by_suppression if plan.suppression_plan else 0
            total_contribution = sourcing_contribution + suppression_contribution
            
            summary.append({
                'entity_id': plan.entity_id,
                'pattern_type': plan.pattern_name,
                'current_t30_gms': f"{plan.current_t30_gms:,.0f}",
                'target_t30_gms': f"{plan.target_t30_gms:,.0f}",
                'gap': f"{plan.total_gap:,.0f}",
                'sourcing_contribution': f"{sourcing_contribution:,.0f}",
                'suppression_contribution': f"{suppression_contribution:,.0f}",
                'total_contribution': f"{total_contribution:,.0f}",
                'feasibility_score': f"{plan.feasibility_score:.1%}"
            })
        
        return jsonify({
            'success': True,
            'message': f'{len(all_plans)}件のプランを生成しました',
            'plans': summary,
            'files': {
                'summary_csv': str(summary_csv),
                'excel': str(excel_file)
            }
        })
    
    except Exception as e:
        traceback.print_exc()
        return jsonify({'success': False, 'message': f'エラー: {str(e)}'})


if __name__ == '__main__':
    print("=" * 50)
    print("Bridge Plan Generator - Web Application")
    print("ブリッジプラン生成ツール - Webアプリ")
    print("=" * 50)
    print()
    print("📂 データを読み込んでいます...")
    
    # Auto-load data on startup
    success, message = load_data()
    if success:
        print(f"✅ {message}")
        print()
        print("🌐 ブラウザで以下のURLを開いてください:")
        print("   http://localhost:5000")
        print()
        print("⚠️  終了するには Ctrl+C を押してください")
    else:
        print(f"❌ {message}")
        print()
        print("⚠️  データ読み込みに失敗しましたが、アプリは起動します")
        print("   ブラウザから手動でデータを読み込んでください")
        print()
        print("🌐 ブラウザで以下のURLを開いてください:")
        print("   http://localhost:5000")
    
    print("=" * 50)
    print()
    
    app.run(debug=True, host='0.0.0.0', port=5000)
