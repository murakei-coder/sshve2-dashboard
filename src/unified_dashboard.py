"""
統合ダッシュボード - すべての分析機能を1つのアプリに統合
"""

from flask import Flask, render_template, request, jsonify, send_file, redirect, url_for
import sys
from pathlib import Path
import pandas as pd
import json
from datetime import datetime
import traceback
import webbrowser
from threading import Timer

# Add src directory to path for imports
src_path = Path(__file__).parent
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

# Bridge Plan Generator imports
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


def load_bridge_data():
    """Load all bridge plan data files and cache them."""
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
    """Main dashboard page."""
    return render_template('unified_dashboard.html')


@app.route('/bridge-plan')
def bridge_plan():
    """Bridge Plan Generator page."""
    return render_template('bridge_plan_app.html')


# Bridge Plan API endpoints
@app.route('/api/bridge/load_data', methods=['POST'])
def api_bridge_load_data():
    """API endpoint to load bridge plan data."""
    success, message = load_bridge_data()
    
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


@app.route('/api/bridge/get_entities', methods=['POST'])
def api_bridge_get_entities():
    """Get list of entities for selected level."""
    data = request.json
    level = data.get('level')
    
    if cached_data['mapping_df'] is None:
        return jsonify({'success': False, 'message': 'データが読み込まれていません'})
    
    try:
        mapping_df = cached_data['mapping_df']
        entities = sorted(mapping_df[level].unique().tolist())
        
        return jsonify({'success': True, 'entities': entities})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})


@app.route('/api/bridge/generate_plan', methods=['POST'])
def api_bridge_generate_plan():
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
            
            # Calculate achievement rate
            achievement_rate = (total_contribution / plan.total_gap * 100) if plan.total_gap > 0 else 0
            
            summary.append({
                'entity_id': plan.entity_id,
                'pattern_type': plan.pattern_name,
                'current_t30_gms': f"{plan.current_t30_gms:,.0f}",
                'target_t30_gms': f"{plan.target_t30_gms:,.0f}",
                'gap': f"{plan.total_gap:,.0f}",
                'sourcing_contribution': f"{sourcing_contribution:,.0f}",
                'suppression_contribution': f"{suppression_contribution:,.0f}",
                'total_contribution': f"{total_contribution:,.0f}",
                'achievement_rate': f"{achievement_rate:.1f}",
                'feasibility_score': f"{plan.feasibility_score:.1%}"
            })
        
        # Prepare detailed statistics
        # Calculate sourcing metrics
        total_asins = len(sourcing_df)
        asins_with_participation = len(sourcing_df[sourcing_df.apply(
            lambda row: any(row[flag] == 'Y' for flag in config.event_flag_priority), axis=1
        )])
        current_sourcing_rate = (asins_with_participation / total_asins * 100) if total_asins > 0 else 0
        
        # Calculate target sourcing rate (assume 80% as target)
        target_sourcing_rate = 80.0
        sourcing_gap = target_sourcing_rate - current_sourcing_rate
        
        # Calculate Promotion OPS
        promotion_ops_calc = promotion_ops_calculator.PromotionOPSCalculator(config.suppression_coefficients)
        
        # Calculate current and target Promotion OPS for the aggregated level
        current_promotion_ops = 0
        target_promotion_ops = 0
        
        for idx, row in aggregated_df.iterrows():
            entity_id_str = str(row[level])
            current_t30_gms = row.get('t30_gms_bau_total', 0)
            target_t30_gms = row.get('t30_gms_target', 0)
            
            # Calculate current Promotion OPS
            current_ops = promotion_ops_calc.calculate_current_promotion_ops(
                current_t30_gms,
                current_suppression_dict
            )
            current_promotion_ops += current_ops
            
            # Calculate target Promotion OPS
            target_ops = promotion_ops_calc.calculate_promotion_ops_target(
                target_t30_gms,
                benchmark_percentages
            )
            target_promotion_ops += target_ops
        
        # Calculate forecasted Promotion OPS (after improvements)
        forecasted_promotion_ops = current_promotion_ops
        for plan in all_plans:
            if plan.suppression_plan:
                forecasted_promotion_ops += plan.suppression_plan.gap_closable_by_suppression
        
        # Prepare detailed suppression breakdown
        suppression_detail = {}
        for category, percentage in current_suppression_dict.items():
            suppression_detail[category] = {
                'current_rate': f"{percentage:.1%}",
                'benchmark_rate': f"{benchmark_percentages.get(category, 0):.1%}",
                'coefficient': f"{config.suppression_coefficients.get(category, 0):.1%}"
            }
        
        detailed_stats = {
            'sourcing': {
                'current_rate': f"{current_sourcing_rate:.1f}%",
                'target_rate': f"{target_sourcing_rate:.1f}%",
                'gap': f"{sourcing_gap:.1f}%",
                'total_asins': total_asins,
                'participating_asins': asins_with_participation,
                'total_cids': len(sourcing_df['CID'].unique()),
                'avg_participation_score': f"{sourcing_df.apply(lambda row: sourcing_processor_obj.calculate_participation_score({flag: row[flag] for flag in config.event_flag_priority}), axis=1).mean():.2f}"
            },
            'suppression': {
                'detail': suppression_detail,
                'benchmark_suppression': {k: f"{v:.1%}" for k, v in benchmark_percentages.items()},
                'current_suppression': {k: f"{v:.1%}" for k, v in current_suppression_dict.items()}
            },
            'promotion_ops': {
                'current_ops': f"{current_promotion_ops:,.0f}",
                'target_ops': f"{target_promotion_ops:,.0f}",
                'forecasted_ops': f"{forecasted_promotion_ops:,.0f}",
                'ops_gap': f"{target_promotion_ops - current_promotion_ops:,.0f}",
                'forecasted_achievement': f"{(forecasted_promotion_ops / target_promotion_ops * 100) if target_promotion_ops > 0 else 0:.1f}%"
            }
        }
        
        return jsonify({
            'success': True,
            'message': f'{len(all_plans)}件のプランを生成しました',
            'plans': summary,
            'detailed_stats': detailed_stats,
            'files': {
                'summary_csv': str(summary_csv),
                'excel': str(excel_file)
            }
        })
    
    except Exception as e:
        traceback.print_exc()
        return jsonify({'success': False, 'message': f'エラー: {str(e)}'})


def open_browser():
    """ブラウザを開く"""
    webbrowser.open('http://localhost:5000')


if __name__ == '__main__':
    print("=" * 50)
    print("統合ダッシュボード - Unified Dashboard")
    print("=" * 50)
    print()
    print("📂 Bridge Planデータを読み込んでいます...")
    
    # Auto-load bridge plan data on startup
    success, message = load_bridge_data()
    if success:
        print(f"✅ {message}")
    else:
        print(f"⚠️  {message}")
        print("   ブラウザから手動でデータを読み込んでください")
    
    print()
    print("🌐 ブラウザで以下のURLを開いてください:")
    print("   http://localhost:5000")
    print()
    print("⚠️  終了するには Ctrl+C を押してください")
    print("=" * 50)
    print()
    
    # Open browser after 1 second
    Timer(1.0, open_browser).start()
    
    app.run(debug=False, host='0.0.0.0', port=5000)
