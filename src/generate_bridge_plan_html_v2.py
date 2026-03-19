"""
Bridge Plan HTMLダッシュボード生成ツール V2
Mockデザインに基づいた新しいレイアウト
"""

import sys
from pathlib import Path
import pandas as pd
import json
from datetime import datetime

# Add src directory to path
src_path = Path(__file__).parent
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

import bridge_config
import bridge_models
from bridge_plan_generator import data_loader
from bridge_plan_generator import sourcing_processor
from bridge_plan_generator import target_processor
from bridge_plan_generator import suppression_processor
from bridge_plan_generator import hierarchy_processor
from bridge_plan_generator import sourcing_plan_generator
from bridge_plan_generator import suppression_plan_generator
from bridge_plan_generator import promotion_ops_calculator
from bridge_plan_generator import bridge_plan_orchestrator


def generate_all_bridge_plans_v2(config_path='config/bridge_config.json'):
    """全てのBridge Planを生成してJSONデータとして返す（V2フォーマット）"""
    
    print("=" * 60)
    print("Bridge Plan HTMLダッシュボード生成 V2")
    print("=" * 60)
    print()
    
    # Load configuration
    print("📂 設定ファイルを読み込んでいます...")
    config = bridge_config.Config.load_from_file(config_path)
    
    # Validate configuration
    is_valid, error_msg = config.validate()
    if not is_valid:
        print(f"❌ 設定ファイルエラー: {error_msg}")
        return None
    
    print("✅ 設定ファイル読み込み完了")
    print()
    
    # Initialize components
    print("📂 データファイルを読み込んでいます...")
    data_loader_obj = data_loader.DataLoader()
    sourcing_processor_obj = sourcing_processor.SourcingProcessor()
    target_processor_obj = target_processor.TargetProcessor()
    suppression_processor_obj = suppression_processor.SuppressionProcessor()
    hierarchy_processor_obj = hierarchy_processor.HierarchyProcessor()
    
    # Load data files
    sourcing_df = data_loader_obj.load_sourcing_data(config.sourcing_data_path)
    target_df = data_loader_obj.load_target_data(config.target_data_path)
    benchmark_df = data_loader_obj.load_suppression_benchmark(config.suppression_benchmark_path)
    mapping_df = data_loader_obj.load_cid_mapping(config.cid_mapping_path, config.cid_mapping_sheet)
    
    print(f"  ✅ Sourcing Data: {len(sourcing_df)} rows")
    print(f"  ✅ Target Data: {len(target_df)} rows")
    print(f"  ✅ Benchmark Data: {len(benchmark_df)} rows")
    print(f"  ✅ CID Mapping: {len(mapping_df)} rows")
    print()
    
    # Build hierarchy map
    hierarchy_map = hierarchy_processor_obj.build_hierarchy_map(mapping_df)
    
    # Process data
    print("🔄 データを処理しています...")
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
    
    print("✅ データ処理完了")
    print()
    
    # Generate plans for CID level only (matching Mock structure)
    print("🎯 Bridge Planを生成しています...")
    all_plans_data = []
    
    level = 'CID'
    aggregated_df = gaps_df
    
    print(f"  📊 {level} レベルを処理中...")
    
    # Initialize plan generators
    promotion_ops_calc = promotion_ops_calculator.PromotionOPSCalculator(config.suppression_coefficients)
    sourcing_generator = sourcing_plan_generator.SourcingPlanGenerator()
    suppression_generator = suppression_plan_generator.SuppressionPlanGenerator(config.suppression_coefficients)
    orchestrator = bridge_plan_orchestrator.BridgePlanOrchestrator(sourcing_generator, suppression_generator)
    
    # Generate plans for each CID
    for idx, row in aggregated_df.iterrows():
        cid = str(row[level])
        current_t30_gms = row.get('t30_gms_bau_total', 0)
        target_t30_gms = row.get('t30_gms_target', 0)
        gap = row.get('gap', 0)
        
        # Get sourcing data for this CID
        entity_sourcing = sourcing_df[sourcing_df['CID'] == cid].copy()
        
        # Add participation scores
        entity_sourcing['participation_score'] = entity_sourcing.apply(
            lambda row: sourcing_processor_obj.calculate_participation_score({
                flag: row[flag] for flag in config.event_flag_priority
            }),
            axis=1
        )
        
        entity_sourcing['t30_gms_bau'] = entity_sourcing['total_t30d_gms_BAU']
        
        # Calculate event participation
        event_participation = {}
        for flag in config.event_flag_priority:
            participated_asins = entity_sourcing[entity_sourcing[flag] == 'Y']
            event_participation[flag] = {
                'asin_count': len(participated_asins),
                'total_gms': float(participated_asins['t30_gms_bau'].sum()) if len(participated_asins) > 0 else 0
            }
        
        # Calculate suppression breakdown
        suppression_breakdown = {}
        if len(entity_sourcing) > 0:
            for category in ['No suppression', 'OOS', 'VRP Missing', 'Price Error', 'Others']:
                category_asins = entity_sourcing[entity_sourcing['suppression_category_large'] == category]
                category_pct = (len(category_asins) / len(entity_sourcing) * 100) if len(entity_sourcing) > 0 else 0
                suppression_breakdown[category] = {
                    'count': len(category_asins),
                    'percentage': float(category_pct)
                }
        
        # Generate Balanced plan (default)
        sourcing_plan = sourcing_generator.generate_plan(gap * 0.5, entity_sourcing)
        suppression_plan = suppression_generator.generate_plan(
            gap * 0.5, current_suppression_dict, benchmark_percentages, target_t30_gms
        )
        
        sourcing_contribution = sourcing_plan.gap_closable_by_sourcing if sourcing_plan else 0
        suppression_contribution = suppression_plan.gap_closable_by_suppression if suppression_plan else 0
        total_contribution = sourcing_contribution + suppression_contribution
        projected_ops = current_t30_gms + total_contribution
        achievement_rate = (projected_ops / target_t30_gms * 100) if target_t30_gms > 0 else 0
        
        plan_data = {
            'cid': cid,
            'current_gms': float(current_t30_gms),
            'target_gms': float(target_t30_gms),
            'gap': float(gap),
            'gap_vs_target_pct': float((gap / target_t30_gms * 100) if target_t30_gms > 0 else 0),
            'event_participation': event_participation,
            'suppression_breakdown': suppression_breakdown,
            'sourcing_improvement': float(sourcing_contribution),
            'suppression_improvement': float(suppression_contribution),
            'suppression_improvement_pct': float((suppression_contribution / current_t30_gms * 100) if current_t30_gms > 0 else 0),
            'projected_ops': float(projected_ops),
            'projected_vs_target': float(projected_ops - target_t30_gms),
            'achievement_rate': float(achievement_rate)
        }
        
        all_plans_data.append(plan_data)
    
    print(f"    ✅ {len(aggregated_df)} CIDs processed")
    print()
    print(f"✅ 合計 {len(all_plans_data)} プランを生成しました")
    print()
    
    # Prepare metadata
    metadata = {
        'generated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'total_plans': len(all_plans_data),
        'suppression_categories': ['No suppression', 'OOS', 'VRP Missing', 'Price Error', 'Others'],
        'event_flags': config.event_flag_priority
    }
    
    return {
        'metadata': metadata,
        'plans': all_plans_data
    }


def generate_html_v2(data, output_path='bridge_plan_dashboard_v2.html'):
    """Mockデザインに基づいたHTMLを生成（インタラクティブ入力機能付き）"""
    
    print("📝 HTMLファイルを生成しています...")
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_filename = f'bridge_plan_dashboard_v2_{timestamp}.html'
    
    # Get suppression coefficients from config
    config = bridge_config.Config.load_from_file('config/bridge_config.json')
    coefficients = config.suppression_coefficients
    
    html_content = f"""<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Bridge Plan Dashboard V2</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', 'Yu Gothic', 'Meiryo', sans-serif;
            background: #f5f7fa;
            padding: 20px;
        }}
        
        .container {{
            max-width: 1800px;
            margin: 0 auto;
            background: white;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            overflow: hidden;
        }}
        
        .header {{
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            color: white;
            padding: 25px 30px;
        }}
        
        .header h1 {{
            font-size: 1.8em;
            margin-bottom: 5px;
        }}
        
        .header p {{
            font-size: 0.9em;
            opacity: 0.9;
        }}
        
        .content {{
            padding: 30px;
        }}
        
        .filter-section {{
            background: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 25px;
            border-left: 4px solid #1e3c72;
        }}
        
        .filter-row {{
            display: flex;
            gap: 15px;
            align-items: flex-end;
        }}
        
        .filter-group {{
            flex: 1;
        }}
        
        .filter-group label {{
            display: block;
            font-weight: 600;
            margin-bottom: 5px;
            color: #333;
            font-size: 0.9em;
        }}
        
        .filter-group input,
        .filter-group select {{
            width: 100%;
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 5px;
            font-size: 0.95em;
        }}
        
        .btn {{
            background: #1e3c72;
            color: white;
            border: none;
            padding: 10px 25px;
            border-radius: 5px;
            cursor: pointer;
            font-weight: 600;
            transition: background 0.3s;
        }}
        
        .btn:hover {{
            background: #2a5298;
        }}
        
        .btn-secondary {{
            background: #6c757d;
        }}
        
        .btn-secondary:hover {{
            background: #5a6268;
        }}
        
        .table-container {{
            overflow-x: auto;
            margin-top: 20px;
        }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 0.9em;
        }}
        
        thead {{
            background: #1e3c72;
            color: white;
        }}
        
        thead th {{
            padding: 12px 8px;
            text-align: center;
            font-weight: 600;
            border-right: 1px solid rgba(255,255,255,0.2);
            font-size: 0.85em;
        }}
        
        thead th:last-child {{
            border-right: none;
        }}
        
        tbody td {{
            padding: 10px 8px;
            text-align: right;
            border-bottom: 1px solid #e9ecef;
            border-right: 1px solid #e9ecef;
        }}
        
        tbody td:first-child {{
            text-align: left;
            font-weight: 600;
            background: #f8f9fa;
        }}
        
        tbody td:last-child {{
            border-right: none;
        }}
        
        tbody tr:hover {{
            background: #f8f9fa;
        }}
        
        .editable-cell {{
            background: #fff9e6 !important;
            cursor: pointer;
            position: relative;
        }}
        
        .editable-cell:hover {{
            background: #fff3cd !important;
        }}
        
        .editable-cell input {{
            width: 100%;
            padding: 5px;
            border: 2px solid #ffc107;
            border-radius: 3px;
            text-align: right;
            font-family: 'Consolas', 'Monaco', monospace;
        }}
        
        .calculated-cell {{
            background: #e7f3ff !important;
            font-weight: 700;
        }}
        
        .positive {{
            color: #28a745;
            font-weight: 600;
        }}
        
        .negative {{
            color: #dc3545;
            font-weight: 600;
        }}
        
        .section-header {{
            background: #e9ecef;
            font-weight: 700;
            text-align: center !important;
        }}
        
        .sub-header {{
            background: #f8f9fa;
            font-weight: 600;
            font-size: 0.8em;
        }}
        
        .number {{
            font-family: 'Consolas', 'Monaco', monospace;
        }}
        
        .pct {{
            font-size: 0.85em;
            color: #666;
        }}
        
        .info-box {{
            background: #e7f3ff;
            border-left: 4px solid #0066cc;
            padding: 15px;
            margin-bottom: 20px;
            border-radius: 5px;
        }}
        
        .hidden {{
            display: none;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎯 Bridge Plan Dashboard V2</h1>
            <p>生成日時: {data['metadata']['generated_at']}</p>
        </div>
        
        <div class="content">
            <div class="info-box">
                <strong>📌 使い方:</strong> CIDを入力して「検索」ボタンをクリックしてください。空欄の場合は全CIDを表示します。
            </div>
            
            <div class="filter-section">
                <div class="filter-row">
                    <div class="filter-group">
                        <label>CID検索</label>
                        <input type="text" id="cidSearch" placeholder="CIDを入力（例: CID001）">
                    </div>
                    <button class="btn" onclick="filterData()">🔍 検索</button>
                    <button class="btn btn-secondary" onclick="resetFilter()">🔄 リセット</button>
                </div>
            </div>
            
            <div id="resultsSection">
                <div class="table-container">
                    <table id="dataTable">
                        <thead>
                            <tr>
                                <th rowspan="2">CID</th>
                                <th colspan="2" class="section-header">Sourced GMS</th>
                                <th colspan="2" class="section-header">過去参加ASIN</th>
                                <th colspan="5" class="section-header">SS HVE1 Suppression rate</th>
                                <th colspan="2" class="section-header">Promotion OPS</th>
                                <th rowspan="2">Sourcing<br>改善幅</th>
                                <th rowspan="2">Suppression<br>改善幅</th>
                                <th rowspan="2">Projected<br>OPS</th>
                            </tr>
                            <tr>
                                <th class="sub-header">Act</th>
                                <th class="sub-header">vs Target</th>
                                <th class="sub-header">SS HVE1</th>
                                <th class="sub-header">T365</th>
                                <th class="sub-header">No Supp</th>
                                <th class="sub-header">OOS</th>
                                <th class="sub-header">VRP Miss</th>
                                <th class="sub-header">Price Err</th>
                                <th class="sub-header">Others</th>
                                <th class="sub-header">Forecast</th>
                                <th class="sub-header">vs Target</th>
                            </tr>
                        </thead>
                        <tbody id="tableBody">
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    </div>
    
    <script>
        const DATA = {json.dumps(data, ensure_ascii=False, indent=2)};
        
        function formatNumber(num) {{
            return Math.round(num).toLocaleString('ja-JP');
        }}
        
        function formatPercent(num) {{
            return num.toFixed(1) + '%';
        }}
        
        function renderTable(plans) {{
            const tbody = document.getElementById('tableBody');
            tbody.innerHTML = '';
            
            plans.forEach(plan => {{
                const row = document.createElement('tr');
                
                // CID
                row.innerHTML = `<td>${{plan.cid}}</td>`;
                
                // Sourced GMS - Act
                row.innerHTML += `<td class="number">${{formatNumber(plan.current_gms)}}</td>`;
                
                // Sourced GMS - vs Target
                const vsTargetClass = plan.gap < 0 ? 'positive' : 'negative';
                row.innerHTML += `<td class="number ${{vsTargetClass}}">${{formatNumber(-plan.gap)}}<br><span class="pct">${{formatPercent(-plan.gap_vs_target_pct)}}</span></td>`;
                
                // 過去参加ASIN - SS HVE1
                const sshve1 = plan.event_participation['sshve1_flag'] || {{asin_count: 0}};
                row.innerHTML += `<td class="number">${{sshve1.asin_count}}</td>`;
                
                // 過去参加ASIN - T365
                const t365 = plan.event_participation['t365_flag'] || {{asin_count: 0}};
                row.innerHTML += `<td class="number">${{t365.asin_count}}</td>`;
                
                // Suppression rates
                const suppCategories = ['No suppression', 'OOS', 'VRP Missing', 'Price Error', 'Others'];
                suppCategories.forEach(cat => {{
                    const suppData = plan.suppression_breakdown[cat] || {{percentage: 0}};
                    row.innerHTML += `<td class="number">${{formatPercent(suppData.percentage)}}</td>`;
                }});
                
                // Promotion OPS - Forecast
                row.innerHTML += `<td class="number">${{formatNumber(plan.target_gms)}}</td>`;
                
                // Promotion OPS - vs Target
                const projVsTargetClass = plan.projected_vs_target >= 0 ? 'positive' : 'negative';
                row.innerHTML += `<td class="number ${{projVsTargetClass}}">${{formatNumber(plan.projected_vs_target)}}</td>`;
                
                // Sourcing改善幅
                row.innerHTML += `<td class="number positive">${{formatNumber(plan.sourcing_improvement)}}</td>`;
                
                // Suppression改善幅
                row.innerHTML += `<td class="number positive">${{formatNumber(plan.suppression_improvement)}}<br><span class="pct">${{formatPercent(plan.suppression_improvement_pct)}}</span></td>`;
                
                // Projected OPS
                const achievementClass = plan.achievement_rate >= 100 ? 'positive' : 'negative';
                row.innerHTML += `<td class="number ${{achievementClass}}">${{formatNumber(plan.projected_ops)}}<br><span class="pct">${{formatPercent(plan.achievement_rate)}}</span></td>`;
                
                tbody.appendChild(row);
            }});
        }}
        
        function filterData() {{
            const searchTerm = document.getElementById('cidSearch').value.trim().toUpperCase();
            
            if (searchTerm === '') {{
                renderTable(DATA.plans);
            }} else {{
                const filtered = DATA.plans.filter(plan => 
                    plan.cid.toUpperCase().includes(searchTerm)
                );
                renderTable(filtered);
            }}
        }}
        
        function resetFilter() {{
            document.getElementById('cidSearch').value = '';
            renderTable(DATA.plans);
        }}
        
        // Initial render
        renderTable(DATA.plans);
    </script>
</body>
</html>"""
    
    with open(output_filename, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"✅ HTMLファイルを生成しました: {output_filename}")
    return output_filename


if __name__ == '__main__':
    data = generate_all_bridge_plans_v2()
    if data:
        output_file = generate_html_v2(data)
        print()
        print("=" * 60)
        print("✨ 完了！")
        print("=" * 60)
        print()
        print(f"📁 生成されたファイル: {output_file}")
        print()
        print("📌 使い方:")
        print("  1. HTMLファイルをダブルクリック")
        print("  2. ブラウザで開く")
        print("  3. CIDで検索")
        print()
