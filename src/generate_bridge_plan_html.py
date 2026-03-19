"""
スタンドアロンBridge Plan HTMLダッシュボード生成ツール

このスクリプトは、Rawデータを読み込んで全てのBridge Planを事前計算し、
結果をJavaScriptデータとして埋め込んだ単一のHTMLファイルを生成します。

生成されたHTMLファイルは：
- Pythonやサーバー不要
- ダブルクリックでブラウザで開ける
- 営業担当が自分のCID/Aliasでフィルタリング可能
- デスクトップに置くだけで使える
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
from bridge_plan_generator import hierarchy_processor
from bridge_plan_generator import promotion_ops_calculator
from bridge_plan_generator import sourcing_plan_generator
from bridge_plan_generator import suppression_plan_generator
from bridge_plan_generator import bridge_plan_orchestrator


def generate_all_bridge_plans(config_path='config/bridge_config.json'):
    """全てのBridge Planを生成してJSONデータとして返す"""
    
    print("=" * 60)
    print("スタンドアロンBridge Plan HTMLダッシュボード生成")
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
    
    # Generate plans for all levels
    print("🎯 Bridge Planを生成しています...")
    all_plans_data = []
    
    levels = ['CID', 'Alias', 'Mgr', 'Team']
    
    for level in levels:
        print(f"  📊 {level} レベルを処理中...")
        
        # Aggregate to level
        if level == 'CID':
            aggregated_df = gaps_df
        elif level == 'Alias':
            aggregated_df = hierarchy_processor_obj.aggregate_by_alias(gaps_df, hierarchy_map)
        elif level == 'Mgr':
            aggregated_df = hierarchy_processor_obj.aggregate_by_manager(gaps_df, hierarchy_map)
        elif level == 'Team':
            aggregated_df = hierarchy_processor_obj.aggregate_by_team(gaps_df, hierarchy_map)
        
        # Initialize plan generators
        promotion_ops_calc = promotion_ops_calculator.PromotionOPSCalculator(config.suppression_coefficients)
        sourcing_generator = sourcing_plan_generator.SourcingPlanGenerator()
        suppression_generator = suppression_plan_generator.SuppressionPlanGenerator(config.suppression_coefficients)
        orchestrator = bridge_plan_orchestrator.BridgePlanOrchestrator(sourcing_generator, suppression_generator)
        
        # Generate plans for each entity
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
            
            # Generate all patterns (force all 3 patterns)
            patterns = []
            
            # Pattern 1: Sourcing-Focused
            sourcing_plan = sourcing_generator.generate_plan(gap, entity_sourcing)
            patterns.append(bridge_models.BridgePlan(
                pattern_name="Sourcing-Focused",
                aggregation_level=level,
                entity_id=entity_id_str,
                current_t30_gms=current_t30_gms,
                target_t30_gms=target_t30_gms,
                total_gap=gap,
                sourcing_plan=sourcing_plan,
                suppression_plan=None,
                feasibility_score=min(1.0, sourcing_plan.gap_closable_by_sourcing / gap) if gap > 0 else 0,
                recommendations=[]
            ))
            
            # Pattern 2: Suppression-Focused
            suppression_plan = suppression_generator.generate_plan(
                gap, current_suppression_dict, benchmark_percentages, target_t30_gms
            )
            patterns.append(bridge_models.BridgePlan(
                pattern_name="Suppression-Focused",
                aggregation_level=level,
                entity_id=entity_id_str,
                current_t30_gms=current_t30_gms,
                target_t30_gms=target_t30_gms,
                total_gap=gap,
                sourcing_plan=None,
                suppression_plan=suppression_plan,
                feasibility_score=min(1.0, suppression_plan.gap_closable_by_suppression / gap) if gap > 0 else 0,
                recommendations=[]
            ))
            
            # Pattern 3: Balanced
            sourcing_plan_balanced = sourcing_generator.generate_plan(gap * 0.5, entity_sourcing)
            suppression_plan_balanced = suppression_generator.generate_plan(
                gap * 0.5, current_suppression_dict, benchmark_percentages, target_t30_gms
            )
            patterns.append(bridge_models.BridgePlan(
                pattern_name="Balanced",
                aggregation_level=level,
                entity_id=entity_id_str,
                current_t30_gms=current_t30_gms,
                target_t30_gms=target_t30_gms,
                total_gap=gap,
                sourcing_plan=sourcing_plan_balanced,
                suppression_plan=suppression_plan_balanced,
                feasibility_score=min(1.0, (sourcing_plan_balanced.gap_closable_by_sourcing + suppression_plan_balanced.gap_closable_by_suppression) / gap) if gap > 0 else 0,
                recommendations=[]
            ))
            
            # Convert to JSON-serializable format with detailed breakdown
            for plan in patterns:
                sourcing_contribution = plan.sourcing_plan.gap_closable_by_sourcing if plan.sourcing_plan else 0
                suppression_contribution = plan.suppression_plan.gap_closable_by_suppression if plan.suppression_plan else 0
                total_contribution = sourcing_contribution + suppression_contribution
                achievement_rate = (total_contribution / plan.total_gap * 100) if plan.total_gap > 0 else 0
                
                # Collect event-specific sourcing details
                event_breakdown = {}
                if plan.sourcing_plan and len(plan.sourcing_plan.recommended_asins) > 0:
                    for flag in config.event_flag_priority:
                        event_asins = entity_sourcing[entity_sourcing[flag] == 'Y']
                        event_breakdown[flag] = {
                            'asin_count': len(event_asins),
                            'total_gms': float(event_asins['t30_gms_bau'].sum()) if len(event_asins) > 0 else 0
                        }
                
                # Collect suppression category details for this entity
                suppression_breakdown = {}
                if level == 'CID':
                    entity_sourcing_for_supp = sourcing_df[sourcing_df['CID'] == entity_id_str]
                else:
                    entity_sourcing_for_supp = entity_sourcing
                
                if len(entity_sourcing_for_supp) > 0:
                    for category in current_suppression_dict.keys():
                        if category == 'No suppression':
                            category_count = len(entity_sourcing_for_supp[entity_sourcing_for_supp['suppression_category_large'] == category])
                        else:
                            category_count = len(entity_sourcing_for_supp[entity_sourcing_for_supp['suppression_category_large'] == category])
                        
                        category_pct = (category_count / len(entity_sourcing_for_supp) * 100) if len(entity_sourcing_for_supp) > 0 else 0
                        suppression_breakdown[category] = {
                            'count': category_count,
                            'percentage': float(category_pct)
                        }
                
                plan_data = {
                    'level': level,
                    'entity_id': plan.entity_id,
                    'pattern_name': plan.pattern_name,
                    'current_t30_gms': float(plan.current_t30_gms),
                    'target_t30_gms': float(plan.target_t30_gms),
                    'gap': float(plan.total_gap),
                    'sourcing_contribution': float(sourcing_contribution),
                    'suppression_contribution': float(suppression_contribution),
                    'total_contribution': float(total_contribution),
                    'achievement_rate': float(achievement_rate),
                    'feasibility_score': float(plan.feasibility_score),
                    'event_breakdown': event_breakdown,
                    'suppression_breakdown': suppression_breakdown
                }
                
                all_plans_data.append(plan_data)
        
        print(f"    ✅ {len(aggregated_df)} entities processed")
    
    print()
    print(f"✅ 合計 {len(all_plans_data)} プランを生成しました")
    print()
    
    # Prepare metadata
    metadata = {
        'generated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'total_plans': len(all_plans_data),
        'levels': levels,
        'suppression_categories': list(current_suppression_dict.keys()),
        'current_suppression': {k: float(v) for k, v in current_suppression_dict.items()},
        'benchmark_suppression': {k: float(v) for k, v in benchmark_percentages.items()},
        'coefficients': config.suppression_coefficients
    }
    
    return {
        'metadata': metadata,
        'plans': all_plans_data
    }


def generate_standalone_html(data, output_path='bridge_plan_standalone.html'):
    """スタンドアロンHTMLファイルを生成"""
    
    print("📝 HTMLファイルを生成しています...")
    
    html_content = f"""<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Bridge Plan Dashboard - スタンドアロン版</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}
        
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
        }}
        
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }}
        
        .header h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
        }}
        
        .header p {{
            font-size: 1.1em;
            opacity: 0.9;
        }}
        
        .content {{
            padding: 40px;
        }}
        
        .filters {{
            background: #f8f9fa;
            padding: 30px;
            border-radius: 15px;
            margin-bottom: 30px;
            border-left: 5px solid #667eea;
        }}
        
        .filter-row {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }}
        
        .filter-group {{
            display: flex;
            flex-direction: column;
        }}
        
        .filter-group label {{
            font-weight: bold;
            margin-bottom: 8px;
            color: #667eea;
        }}
        
        .filter-group select {{
            padding: 12px;
            font-size: 1em;
            border: 2px solid #e0e0e0;
            border-radius: 8px;
            transition: border-color 0.3s;
        }}
        
        .filter-group select:focus {{
            outline: none;
            border-color: #667eea;
        }}
        
        .button {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 12px 30px;
            font-size: 1em;
            border-radius: 50px;
            cursor: pointer;
            transition: transform 0.2s, box-shadow 0.2s;
            font-weight: bold;
        }}
        
        .button:hover {{
            transform: translateY(-2px);
            box-shadow: 0 10px 20px rgba(102, 126, 234, 0.4);
        }}
        
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        
        .stat-card {{
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            text-align: center;
        }}
        
        .stat-card .number {{
            font-size: 2.5em;
            font-weight: bold;
            color: #667eea;
            margin-bottom: 10px;
        }}
        
        .stat-card .label {{
            color: #666;
            font-size: 1.1em;
        }}
        
        .results-table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
            background: white;
            border-radius: 10px;
            overflow: hidden;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        
        .results-table th {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 15px;
            text-align: left;
            font-weight: bold;
        }}
        
        .results-table td {{
            padding: 12px 15px;
            border-bottom: 1px solid #e0e0e0;
        }}
        
        .results-table tr:hover {{
            background: #f8f9fa;
        }}
        
        .info-box {{
            background: #e3f2fd;
            border-left: 4px solid #2196f3;
            padding: 15px;
            margin: 20px 0;
            border-radius: 5px;
        }}
        
        .info-box strong {{
            color: #1976d2;
        }}
        
        .hidden {{
            display: none;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎯 Bridge Plan Dashboard</h1>
            <p>ブリッジプラン分析ダッシュボード（スタンドアロン版）</p>
            <p style="font-size: 0.9em; margin-top: 10px;">生成日時: {data['metadata']['generated_at']}</p>
        </div>
        
        <div class="content">
            <div class="info-box">
                <strong>📌 使い方:</strong> 集計レベルと対象を選択して「表示」ボタンをクリックしてください。
                このファイルはオフラインで動作します（インターネット接続不要）。
            </div>
            
            <div class="filters">
                <h2 style="margin-bottom: 20px; color: #667eea;">🔍 フィルター</h2>
                <div class="filter-row">
                    <div class="filter-group">
                        <label>集計レベル</label>
                        <select id="levelSelect" onchange="updateEntityOptions()">
                            <option value="">-- 選択してください --</option>
                            <option value="CID">CID（個別セラー）</option>
                            <option value="Alias">Alias（営業担当者）</option>
                            <option value="Mgr">Mgr（マネージャー）</option>
                            <option value="Team">Team（チーム）</option>
                        </select>
                    </div>
                    
                    <div class="filter-group">
                        <label>対象（オプション）</label>
                        <select id="entitySelect">
                            <option value="">すべて</option>
                        </select>
                    </div>
                    
                    <div class="filter-group">
                        <label>パターン（オプション）</label>
                        <select id="patternSelect">
                            <option value="">すべて</option>
                            <option value="Sourcing-Focused">Sourcing-Focused</option>
                            <option value="Suppression-Focused">Suppression-Focused</option>
                            <option value="Balanced">Balanced</option>
                        </select>
                    </div>
                </div>
                
                <button class="button" onclick="filterAndDisplay()">📊 表示</button>
                <button class="button" onclick="resetFilters()" style="margin-left: 10px; background: #6c757d;">🔄 リセット</button>
            </div>
            
            <div id="statsSection" class="hidden">
                <h2 style="margin-bottom: 20px; color: #667eea;">📈 統計サマリー</h2>
                <div class="stats-grid" id="statsGrid"></div>
            </div>
            
            <div id="resultsSection" class="hidden">
                <h2 style="margin-bottom: 20px; color: #667eea;">📋 Bridge Plan一覧</h2>
                <div id="resultsCount" style="margin-bottom: 15px; font-weight: bold;"></div>
                <div style="overflow-x: auto;">
                    <table class="results-table">
                        <thead>
                            <tr>
                                <th>レベル</th>
                                <th>対象</th>
                                <th>パターン</th>
                                <th>現在GMS</th>
                                <th>目標GMS</th>
                                <th>ギャップ</th>
                                <th>Sourcing貢献</th>
                                <th>Suppression改善</th>
                                <th>合計貢献</th>
                                <th>達成率</th>
                                <th>詳細</th>
                            </tr>
                        </thead>
                        <tbody id="resultsBody">
                        </tbody>
                    </table>
                </div>
            </div>
            
            <!-- Detail Modal -->
            <div id="detailModal" class="modal hidden">
                <div class="modal-content">
                    <span class="close" onclick="closeDetailModal()">&times;</span>
                    <h2 id="modalTitle"></h2>
                    <div id="modalBody"></div>
                </div>
            </div>
        </div>
    </div>
    
    <style>
        .modal {{
            display: none;
            position: fixed;
            z-index: 1000;
            left: 0;
            top: 0;
            width: 100%;
            height: 100%;
            overflow: auto;
            background-color: rgba(0,0,0,0.6);
        }}
        
        .modal.show {{
            display: block;
        }}
        
        .modal-content {{
            background-color: #fefefe;
            margin: 5% auto;
            padding: 30px;
            border: 1px solid #888;
            border-radius: 15px;
            width: 90%;
            max-width: 1000px;
            max-height: 80vh;
            overflow-y: auto;
        }}
        
        .close {{
            color: #aaa;
            float: right;
            font-size: 28px;
            font-weight: bold;
            cursor: pointer;
        }}
        
        .close:hover,
        .close:focus {{
            color: #000;
        }}
        
        .detail-section {{
            margin: 20px 0;
            padding: 20px;
            background: #f8f9fa;
            border-radius: 10px;
        }}
        
        .detail-section h3 {{
            color: #667eea;
            margin-bottom: 15px;
        }}
        
        .detail-table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 10px;
        }}
        
        .detail-table th,
        .detail-table td {{
            padding: 10px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }}
        
        .detail-table th {{
            background: #667eea;
            color: white;
        }}
        
        .btn-detail {{
            background: #667eea;
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 5px;
            cursor: pointer;
            font-size: 0.9em;
        }}
        
        .btn-detail:hover {{
            background: #5568d3;
        }}
    </style>
    
    <script>
        // Embed data
        const BRIDGE_PLAN_DATA = {json.dumps(data, ensure_ascii=False, indent=2)};
        
        function showDetailModal(planIndex) {{
            const plan = window.currentFilteredPlans[planIndex];
            const modal = document.getElementById('detailModal');
            const modalTitle = document.getElementById('modalTitle');
            const modalBody = document.getElementById('modalBody');
            
            modalTitle.textContent = `${{plan.entity_id}} - ${{plan.pattern_name}} 詳細`;
            
            let html = '';
            
            // Sourcing Detail
            if (plan.event_breakdown && Object.keys(plan.event_breakdown).length > 0) {{
                html += `
                    <div class="detail-section">
                        <h3>📊 Sourcingポテンシャル詳細（イベント別）</h3>
                        <table class="detail-table">
                            <thead>
                                <tr>
                                    <th>イベント</th>
                                    <th>参加ASIN数</th>
                                    <th>合計GMS</th>
                                </tr>
                            </thead>
                            <tbody>
                `;
                
                for (const [event, data] of Object.entries(plan.event_breakdown)) {{
                    html += `
                        <tr>
                            <td><strong>${{event}}</strong></td>
                            <td>${{data.asin_count.toLocaleString('ja-JP')}}</td>
                            <td>${{data.total_gms.toLocaleString('ja-JP', {{maximumFractionDigits: 0}})}}</td>
                        </tr>
                    `;
                }}
                
                html += `
                            </tbody>
                        </table>
                        <p style="margin-top: 15px; font-size: 0.9em; color: #666;">
                            ※ 各イベントに過去参加したASINの数とGMS合計を表示しています
                        </p>
                    </div>
                `;
            }}
            
            // Suppression Detail
            if (plan.suppression_breakdown && Object.keys(plan.suppression_breakdown).length > 0) {{
                html += `
                    <div class="detail-section">
                        <h3>📍 Suppression状況詳細（カテゴリ別）</h3>
                        <table class="detail-table">
                            <thead>
                                <tr>
                                    <th>カテゴリ</th>
                                    <th>ASIN数</th>
                                    <th>割合</th>
                                </tr>
                            </thead>
                            <tbody>
                `;
                
                for (const [category, data] of Object.entries(plan.suppression_breakdown)) {{
                    html += `
                        <tr>
                            <td><strong>${{category}}</strong></td>
                            <td>${{data.count.toLocaleString('ja-JP')}}</td>
                            <td>${{data.percentage.toFixed(1)}}%</td>
                        </tr>
                    `;
                }}
                
                html += `
                            </tbody>
                        </table>
                        <p style="margin-top: 15px; font-size: 0.9em; color: #666;">
                            ※ このエンティティのASINがどのSuppressionカテゴリに属しているかを表示しています
                        </p>
                    </div>
                `;
            }}
            
            // Summary
            html += `
                <div class="detail-section">
                    <h3>📈 達成状況サマリー</h3>
                    <table class="detail-table">
                        <tbody>
                            <tr>
                                <td><strong>現在GMS</strong></td>
                                <td>${{plan.current_t30_gms.toLocaleString('ja-JP', {{maximumFractionDigits: 0}})}}</td>
                            </tr>
                            <tr>
                                <td><strong>目標GMS</strong></td>
                                <td>${{plan.target_t30_gms.toLocaleString('ja-JP', {{maximumFractionDigits: 0}})}}</td>
                            </tr>
                            <tr>
                                <td><strong>ギャップ</strong></td>
                                <td>${{plan.gap.toLocaleString('ja-JP', {{maximumFractionDigits: 0}})}}</td>
                            </tr>
                            <tr>
                                <td><strong>Sourcing貢献</strong></td>
                                <td>${{plan.sourcing_contribution.toLocaleString('ja-JP', {{maximumFractionDigits: 0}})}}</td>
                            </tr>
                            <tr>
                                <td><strong>Suppression改善</strong></td>
                                <td>${{plan.suppression_contribution.toLocaleString('ja-JP', {{maximumFractionDigits: 0}})}}</td>
                            </tr>
                            <tr style="background: #f0f0f0;">
                                <td><strong>合計貢献</strong></td>
                                <td><strong>${{plan.total_contribution.toLocaleString('ja-JP', {{maximumFractionDigits: 0}})}}</strong></td>
                            </tr>
                            <tr style="background: ${{plan.achievement_rate >= 100 ? '#d4edda' : '#fff3cd'}};">
                                <td><strong>達成率</strong></td>
                                <td><strong style="color: ${{plan.achievement_rate >= 100 ? '#28a745' : '#ffc107'}}">${{plan.achievement_rate.toFixed(1)}}%</strong></td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            `;
            
            modalBody.innerHTML = html;
            modal.classList.remove('hidden');
            modal.classList.add('show');
        }}
        
        function closeDetailModal() {{
            const modal = document.getElementById('detailModal');
            modal.classList.remove('show');
            modal.classList.add('hidden');
        }}
        
        // Close modal when clicking outside
        window.onclick = function(event) {{
            const modal = document.getElementById('detailModal');
            if (event.target == modal) {{
                closeDetailModal();
            }}
        }}
        
        function updateEntityOptions() {{
            const level = document.getElementById('levelSelect').value;
            const entitySelect = document.getElementById('entitySelect');
            
            entitySelect.innerHTML = '<option value="">すべて</option>';
            
            if (!level) return;
            
            // Get unique entities for this level
            const entities = [...new Set(
                BRIDGE_PLAN_DATA.plans
                    .filter(p => p.level === level)
                    .map(p => p.entity_id)
            )].sort();
            
            entities.forEach(entity => {{
                const option = document.createElement('option');
                option.value = entity;
                option.textContent = entity;
                entitySelect.appendChild(option);
            }});
        }}
        
        function filterAndDisplay() {{
            const level = document.getElementById('levelSelect').value;
            const entity = document.getElementById('entitySelect').value;
            const pattern = document.getElementById('patternSelect').value;
            
            if (!level) {{
                alert('集計レベルを選択してください');
                return;
            }}
            
            // Filter plans
            let filteredPlans = BRIDGE_PLAN_DATA.plans.filter(p => p.level === level);
            
            if (entity) {{
                filteredPlans = filteredPlans.filter(p => p.entity_id === entity);
            }}
            
            if (pattern) {{
                filteredPlans = filteredPlans.filter(p => p.pattern_name === pattern);
            }}
            
            // Store for detail modal
            window.currentFilteredPlans = filteredPlans;
            
            // Display results
            displayResults(filteredPlans);
            displayStats(filteredPlans);
        }}
        
        function displayResults(plans) {{
            const tbody = document.getElementById('resultsBody');
            const resultsSection = document.getElementById('resultsSection');
            const resultsCount = document.getElementById('resultsCount');
            
            tbody.innerHTML = '';
            
            if (plans.length === 0) {{
                tbody.innerHTML = '<tr><td colspan="11" style="text-align: center; padding: 30px;">該当するプランが見つかりません</td></tr>';
                resultsSection.classList.remove('hidden');
                resultsCount.textContent = '0件のプラン';
                return;
            }}
            
            plans.forEach((plan, index) => {{
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td>${{plan.level}}</td>
                    <td><strong>${{plan.entity_id}}</strong></td>
                    <td>${{plan.pattern_name}}</td>
                    <td>${{plan.current_t30_gms.toLocaleString('ja-JP', {{maximumFractionDigits: 0}})}}</td>
                    <td>${{plan.target_t30_gms.toLocaleString('ja-JP', {{maximumFractionDigits: 0}})}}</td>
                    <td>${{plan.gap.toLocaleString('ja-JP', {{maximumFractionDigits: 0}})}}</td>
                    <td>${{plan.sourcing_contribution.toLocaleString('ja-JP', {{maximumFractionDigits: 0}})}}</td>
                    <td>${{plan.suppression_contribution.toLocaleString('ja-JP', {{maximumFractionDigits: 0}})}}</td>
                    <td><strong>${{plan.total_contribution.toLocaleString('ja-JP', {{maximumFractionDigits: 0}})}}</strong></td>
                    <td><strong style="color: ${{plan.achievement_rate >= 100 ? '#28a745' : '#dc3545'}}">${{plan.achievement_rate.toFixed(1)}}%</strong></td>
                    <td><button class="btn-detail" onclick="showDetailModal(${{index}})">詳細</button></td>
                `;
                tbody.appendChild(row);
            }});
            
            resultsSection.classList.remove('hidden');
            resultsCount.textContent = `${{plans.length}}件のプラン`;
        }}
        
        function displayStats(plans) {{
            const statsGrid = document.getElementById('statsGrid');
            const statsSection = document.getElementById('statsSection');
            
            if (plans.length === 0) {{
                statsSection.classList.add('hidden');
                return;
            }}
            
            // Calculate stats
            const totalGap = plans.reduce((sum, p) => sum + p.gap, 0);
            const totalContribution = plans.reduce((sum, p) => sum + p.total_contribution, 0);
            const avgAchievement = plans.reduce((sum, p) => sum + p.achievement_rate, 0) / plans.length;
            const plansOver100 = plans.filter(p => p.achievement_rate >= 100).length;
            
            statsGrid.innerHTML = `
                <div class="stat-card">
                    <div class="number">${{plans.length}}</div>
                    <div class="label">プラン数</div>
                </div>
                <div class="stat-card">
                    <div class="number">${{totalGap.toLocaleString('ja-JP', {{maximumFractionDigits: 0}})}}</div>
                    <div class="label">総ギャップ</div>
                </div>
                <div class="stat-card">
                    <div class="number">${{totalContribution.toLocaleString('ja-JP', {{maximumFractionDigits: 0}})}}</div>
                    <div class="label">総貢献見込み</div>
                </div>
                <div class="stat-card">
                    <div class="number" style="color: ${{avgAchievement >= 100 ? '#28a745' : '#dc3545'}}">${{avgAchievement.toFixed(1)}}%</div>
                    <div class="label">平均達成率</div>
                </div>
                <div class="stat-card">
                    <div class="number" style="color: #28a745">${{plansOver100}}</div>
                    <div class="label">達成可能プラン</div>
                </div>
            `;
            
            statsSection.classList.remove('hidden');
        }}
        
        function resetFilters() {{
            document.getElementById('levelSelect').value = '';
            document.getElementById('entitySelect').innerHTML = '<option value="">すべて</option>';
            document.getElementById('patternSelect').value = '';
            document.getElementById('resultsSection').classList.add('hidden');
            document.getElementById('statsSection').classList.add('hidden');
        }}
    </script>
</body>
</html>"""
    
    # Write to file
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"✅ HTMLファイルを生成しました: {output_path}")
    print()
    print("=" * 60)
    print("✨ 完了！")
    print("=" * 60)
    print()
    print(f"📁 生成されたファイル: {output_path}")
    print()
    print("📌 使い方:")
    print("  1. このHTMLファイルを営業担当に配布")
    print("  2. デスクトップに置いてダブルクリック")
    print("  3. ブラウザで開いて、自分のCID/Aliasでフィルタリング")
    print()
    print("💡 このファイルは:")
    print("  ✅ Pythonインストール不要")
    print("  ✅ サーバー起動不要")
    print("  ✅ インターネット接続不要")
    print("  ✅ ダブルクリックで即使用可能")
    print()


if __name__ == '__main__':
    # Generate all bridge plans
    data = generate_all_bridge_plans()
    
    if data:
        # Generate standalone HTML
        output_file = f"bridge_plan_dashboard_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        generate_standalone_html(data, output_file)
