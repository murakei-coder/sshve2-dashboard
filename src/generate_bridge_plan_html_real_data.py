"""
Bridge Plan HTMLダッシュボード生成ツール - 実データ版
実際のSSHVE2データを使用してインタラクティブダッシュボードを生成
"""

import sys
from pathlib import Path
import pandas as pd
import json
from datetime import datetime
import numpy as np

# Add src directory to path
src_path = Path(__file__).parent
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))


def load_real_data(config_path='config/bridge_config_real.json'):
    """実データを読み込む"""
    
    print("=" * 60)
    print("Bridge Plan インタラクティブダッシュボード生成（実データ版）")
    print("=" * 60)
    print()
    
    # Load configuration
    print("📂 設定ファイルを読み込んでいます...")
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    print("✅ 設定ファイル読み込み完了")
    print()
    
    # Load sourcing data
    print("📂 ソーシングデータを読み込んでいます...")
    sourcing_df = pd.read_csv(config['sourcing_data_path'])
    print(f"  ✅ Sourcing Data: {len(sourcing_df)} rows")
    
    # Load target data
    print("📂 ターゲットデータを読み込んでいます...")
    target_df = pd.read_excel(config['target_data_path'])
    print(f"  ✅ Target Data: {len(target_df)} rows")
    
    # Load suppression benchmark
    print("📂 Suppressionベンチマークを読み込んでいます...")
    suppression_df = pd.read_csv(config['suppression_benchmark_path'])
    print(f"  ✅ Suppression Benchmark: {len(suppression_df)} rows")
    
    # Load CID mapping
    print("📂 CIDマッピングを読み込んでいます...")
    mapping_df = pd.read_excel(config['cid_mapping_path'])
    print(f"  ✅ CID Mapping: {len(mapping_df)} rows")
    print()
    
    return sourcing_df, target_df, suppression_df, mapping_df, config


def process_real_data(sourcing_df, target_df, suppression_df, mapping_df, config):
    """実データを処理してダッシュボード用のデータを生成"""
    
    print("🔄 データを処理しています...")
    
    # Create CID info dictionary
    cid_info = {}
    for _, row in mapping_df.iterrows():
        mcid = str(int(row['mcid']))
        cid_info[mcid] = {
            'alias': str(row.get('Alias', '')),
            'mgr': str(row.get('Mgr', '')),
            'team': str(row.get('Team', ''))
        }
    
    # Create suppression benchmark dictionary
    suppression_benchmark = {}
    for _, row in suppression_df.iterrows():
        mcid = str(int(row['merchant_customer_id'])) if pd.notna(row['merchant_customer_id']) else None
        if mcid:
            suppression_benchmark[mcid] = {
                'No suppression': row.get('current_cat_pct_no_suppression', 0) * 100 if pd.notna(row.get('current_cat_pct_no_suppression')) else 0,
                'OOS': row.get('current_cat_pct_oos', 0) * 100 if pd.notna(row.get('current_cat_pct_oos')) else 0,
                'VRP Missing': row.get('current_cat_pct_vrp_missing', 0) * 100 if pd.notna(row.get('current_cat_pct_vrp_missing')) else 0,
                'Price Error': row.get('current_cat_pct_price_error', 0) * 100 if pd.notna(row.get('current_cat_pct_price_error')) else 0,
                'Others': row.get('current_cat_pct_others', 0) * 100 if pd.notna(row.get('current_cat_pct_others')) else 0
            }
    
    # Process each CID
    all_cid_data = []
    
    # Group by mcid
    for mcid, group in sourcing_df.groupby('mcid'):
        mcid_str = str(int(mcid))
        
        # Get CID info
        info = cid_info.get(mcid_str, {'alias': '', 'mgr': '', 'team': ''})
        
        # Get target data
        target_row = target_df[target_df['mcid'] == mcid]
        if len(target_row) == 0:
            continue
        
        target_row = target_row.iloc[0]
        current_gms = float(target_row.get('total_t30d_gms_BAU', 0))
        target_gms = float(target_row.get('T30 GMS Target', 0))
        gap = target_gms - current_gms
        
        # Calculate event participation
        event_participation = {}
        for flag in config['event_flag_priority']:
            participated_asins = group[group[flag] == 'Y']
            event_participation[flag] = {
                'asin_count': len(participated_asins),
                'total_gms': float(participated_asins['total_t30d_gms_BAU'].sum()) if len(participated_asins) > 0 else 0
            }
        
        # Get suppression breakdown from benchmark
        suppression_breakdown = suppression_benchmark.get(mcid_str, {
            'No suppression': 0,
            'OOS': 0,
            'VRP Missing': 0,
            'Price Error': 0,
            'Others': 0
        })
        
        # Convert to the format expected by the HTML
        suppression_breakdown_formatted = {}
        for category, percentage in suppression_breakdown.items():
            suppression_breakdown_formatted[category] = {
                'count': 0,  # Not available in this data
                'percentage': float(percentage)
            }
        
        cid_data = {
            'cid': mcid_str,
            'alias': info['alias'],
            'mgr': info['mgr'],
            'team': info['team'],
            'current_gms': float(current_gms),
            'target_gms': float(target_gms),
            'gap': float(gap),
            'event_participation': event_participation,
            'suppression_breakdown': suppression_breakdown_formatted
        }
        
        all_cid_data.append(cid_data)
    
    print(f"    ✅ {len(all_cid_data)} CIDs processed")
    print()
    
    # Prepare metadata
    metadata = {
        'generated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'total_cids': len(all_cid_data),
        'suppression_coefficients': config['suppression_coefficients'],
        'event_flags': config['event_flag_priority']
    }
    
    return {
        'metadata': metadata,
        'cids': all_cid_data
    }


def generate_interactive_html(data):
    """インタラクティブHTMLを生成"""
    
    print("📝 HTMLファイルを生成しています...")
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_filename = f'bridge_plan_interactive_real_{timestamp}.html'
    
    coefficients = data['metadata']['suppression_coefficients']
    
    html_content = f"""<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Bridge Plan インタラクティブダッシュボード（実データ）</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        
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
        
        .header h1 {{ font-size: 1.8em; margin-bottom: 5px; }}
        .header p {{ font-size: 0.9em; opacity: 0.9; }}
        
        .content {{ padding: 30px; }}
        
        .info-box {{
            background: #fff3cd;
            border-left: 4px solid #ffc107;
            padding: 15px;
            margin-bottom: 20px;
            border-radius: 5px;
        }}
        
        .info-box strong {{ color: #856404; }}
        
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
            flex-wrap: wrap;
        }}
        
        .filter-group {{ flex: 1; min-width: 150px; }}
        
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
        
        .btn:hover {{ background: #2a5298; }}
        .btn-secondary {{ background: #6c757d; }}
        .btn-secondary:hover {{ background: #5a6268; }}
        
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
        
        tbody td:nth-child(2),
        tbody td:nth-child(3),
        tbody td:nth-child(4) {{
            text-align: left;
            background: #f8f9fa;
        }}
        
        tbody tr:hover {{ background: #f8f9fa; }}
        
        .editable-cell {{
            background: #fff9e6 !important;
            cursor: pointer;
        }}
        
        .editable-cell:hover {{ background: #fff3cd !important; }}
        
        .editable-cell input {{
            width: 100%;
            padding: 5px;
            border: 2px solid #ffc107;
            border-radius: 3px;
            text-align: right;
            font-family: 'Consolas', 'Monaco', monospace;
            font-size: 0.9em;
        }}
        
        .calculated-cell {{
            background: #e7f3ff !important;
            font-weight: 700;
        }}
        
        .positive {{ color: #28a745; font-weight: 600; }}
        .negative {{ color: #dc3545; font-weight: 600; }}
        .section-header {{ background: #e9ecef; font-weight: 700; }}
        .sub-header {{ background: #f8f9fa; font-weight: 600; font-size: 0.8em; }}
        .number {{ font-family: 'Consolas', 'Monaco', monospace; }}
        .pct {{ font-size: 0.85em; color: #666; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎯 Bridge Plan インタラクティブダッシュボード（実データ）</h1>
            <p>生成日時: {data['metadata']['generated_at']} | 総CID数: {data['metadata']['total_cids']}</p>
        </div>
        
        <div class="content">
            <div class="info-box">
                <strong>💡 使い方:</strong><br>
                1. CID、Alias、Mgr、Teamで検索してフィルター<br>
                2. 黄色のセル（Sourcing改善幅、Price Error削減率）をクリックして値を入力<br>
                3. Projected OPSが自動計算されます
            </div>
            
            <div class="filter-section">
                <div class="filter-row">
                    <div class="filter-group">
                        <label>CID検索</label>
                        <input type="text" id="cidSearch" placeholder="CIDを入力">
                    </div>
                    <div class="filter-group">
                        <label>Alias検索</label>
                        <input type="text" id="aliasSearch" placeholder="Aliasを入力">
                    </div>
                    <div class="filter-group">
                        <label>Mgr検索</label>
                        <input type="text" id="mgrSearch" placeholder="Mgrを入力">
                    </div>
                    <div class="filter-group">
                        <label>Team検索</label>
                        <input type="text" id="teamSearch" placeholder="Teamを入力">
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
                                <th rowspan="2">Alias</th>
                                <th rowspan="2">Mgr</th>
                                <th rowspan="2">Team</th>
                                <th colspan="2" class="section-header">Sourced GMS</th>
                                <th colspan="2" class="section-header">過去参加ASIN</th>
                                <th colspan="5" class="section-header">Suppression Rate</th>
                                <th colspan="2" class="section-header">Promotion OPS</th>
                                <th rowspan="2">Sourcing<br>改善幅<br>(入力)</th>
                                <th rowspan="2">Price Error<br>削減率%<br>(入力)</th>
                                <th rowspan="2">Projected<br>OPS<br>(計算)</th>
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
        const COEFFICIENTS = {json.dumps(coefficients, ensure_ascii=False)};
        
        // Store user inputs
        const userInputs = {{}};
        
        function formatNumber(num) {{
            return Math.round(num).toLocaleString('ja-JP');
        }}
        
        function formatPercent(num) {{
            return num.toFixed(1) + '%';
        }}
        
        function calculateProjectedOPS(cid, currentGMS, targetGMS, suppBreakdown) {{
            const inputs = userInputs[cid] || {{}};
            const sourcingImprovement = parseFloat(inputs.sourcing || 0);
            const priceErrorReduction = parseFloat(inputs.priceErrorReduction || 0);
            
            // Calculate suppression improvement
            // Formula: Current GMS * (Price Error % * Reduction % * Coefficient)
            const currentPriceErrorPct = suppBreakdown['Price Error'].percentage / 100;
            const priceErrorReductionPct = priceErrorReduction / 100;
            const coefficient = COEFFICIENTS['Price Error'];
            
            const suppressionImprovement = currentGMS * currentPriceErrorPct * priceErrorReductionPct * coefficient;
            
            // Projected OPS = Current GMS + Sourcing Improvement + Suppression Improvement
            const projectedOPS = currentGMS + sourcingImprovement + suppressionImprovement;
            
            return {{
                sourcingImprovement: sourcingImprovement,
                suppressionImprovement: suppressionImprovement,
                projectedOPS: projectedOPS,
                vsTarget: projectedOPS - targetGMS,
                achievementRate: (projectedOPS / targetGMS * 100)
            }};
        }}
        
        function makeEditable(cell, cid, field) {{
            const currentValue = userInputs[cid]?.[field] || 0;
            cell.innerHTML = `<input type="number" value="${{currentValue}}" 
                onblur="updateValue('${{cid}}', '${{field}}', this.value)" 
                onkeypress="if(event.key==='Enter') this.blur()" 
                step="0.01" min="0">`;
            cell.querySelector('input').focus();
            cell.querySelector('input').select();
        }}
        
        function updateValue(cid, field, value) {{
            if (!userInputs[cid]) {{
                userInputs[cid] = {{}};
            }}
            userInputs[cid][field] = parseFloat(value) || 0;
            renderTable(window.currentPlans);
        }}
        
        function renderTable(plans) {{
            const tbody = document.getElementById('tableBody');
            tbody.innerHTML = '';
            
            window.currentPlans = plans;
            
            plans.forEach(plan => {{
                const row = document.createElement('tr');
                
                const calc = calculateProjectedOPS(
                    plan.cid, 
                    plan.current_gms, 
                    plan.target_gms, 
                    plan.suppression_breakdown
                );
                
                // CID
                const cidCell = document.createElement('td');
                cidCell.textContent = plan.cid;
                row.appendChild(cidCell);
                
                // Alias
                const aliasCell = document.createElement('td');
                aliasCell.textContent = plan.alias;
                row.appendChild(aliasCell);
                
                // Mgr
                const mgrCell = document.createElement('td');
                mgrCell.textContent = plan.mgr;
                row.appendChild(mgrCell);
                
                // Team
                const teamCell = document.createElement('td');
                teamCell.textContent = plan.team;
                row.appendChild(teamCell);
                
                // Sourced GMS - Act
                const actCell = document.createElement('td');
                actCell.className = 'number';
                actCell.textContent = formatNumber(plan.current_gms);
                row.appendChild(actCell);
                
                // Sourced GMS - vs Target
                const vsTargetClass = plan.gap < 0 ? 'positive' : 'negative';
                const vsTargetCell = document.createElement('td');
                vsTargetCell.className = 'number ' + vsTargetClass;
                vsTargetCell.innerHTML = `${{formatNumber(-plan.gap)}}<br><span class="pct">${{formatPercent(-plan.gap / plan.target_gms * 100)}}</span>`;
                row.appendChild(vsTargetCell);
                
                // 過去参加ASIN - SS HVE1
                const sshve1 = plan.event_participation['sshve1_flag'] || {{asin_count: 0}};
                const sshve1Cell = document.createElement('td');
                sshve1Cell.className = 'number';
                sshve1Cell.textContent = sshve1.asin_count;
                row.appendChild(sshve1Cell);
                
                // 過去参加ASIN - T365
                const t365 = plan.event_participation['t365_flag'] || {{asin_count: 0}};
                const t365Cell = document.createElement('td');
                t365Cell.className = 'number';
                t365Cell.textContent = t365.asin_count;
                row.appendChild(t365Cell);
                
                // Suppression rates
                const suppCategories = ['No suppression', 'OOS', 'VRP Missing', 'Price Error', 'Others'];
                suppCategories.forEach(cat => {{
                    const suppData = plan.suppression_breakdown[cat] || {{percentage: 0}};
                    const suppCell = document.createElement('td');
                    suppCell.className = 'number';
                    suppCell.textContent = formatPercent(suppData.percentage);
                    row.appendChild(suppCell);
                }});
                
                // Promotion OPS - Forecast
                const forecastCell = document.createElement('td');
                forecastCell.className = 'number';
                forecastCell.textContent = formatNumber(plan.target_gms);
                row.appendChild(forecastCell);
                
                // Promotion OPS - vs Target
                const projVsTargetClass = calc.vsTarget >= 0 ? 'positive' : 'negative';
                const projVsTargetCell = document.createElement('td');
                projVsTargetCell.className = 'number ' + projVsTargetClass;
                projVsTargetCell.textContent = formatNumber(calc.vsTarget);
                row.appendChild(projVsTargetCell);
                
                // Sourcing改善幅 (Editable)
                const sourcingCell = document.createElement('td');
                sourcingCell.className = 'number editable-cell';
                sourcingCell.textContent = formatNumber(calc.sourcingImprovement);
                sourcingCell.onclick = function() {{ makeEditable(this, plan.cid, 'sourcing'); }};
                row.appendChild(sourcingCell);
                
                // Price Error削減率 (Editable)
                const priceErrorReduction = userInputs[plan.cid]?.priceErrorReduction || 0;
                const priceErrorCell = document.createElement('td');
                priceErrorCell.className = 'number editable-cell';
                priceErrorCell.textContent = formatPercent(priceErrorReduction);
                priceErrorCell.onclick = function() {{ makeEditable(this, plan.cid, 'priceErrorReduction'); }};
                row.appendChild(priceErrorCell);
                
                // Projected OPS (Calculated)
                const achievementClass = calc.achievementRate >= 100 ? 'positive' : 'negative';
                const projectedCell = document.createElement('td');
                projectedCell.className = 'number calculated-cell ' + achievementClass;
                projectedCell.innerHTML = `${{formatNumber(calc.projectedOPS)}}<br><span class="pct">${{formatPercent(calc.achievementRate)}}</span>`;
                row.appendChild(projectedCell);
                
                tbody.appendChild(row);
            }});
        }}
        
        function filterData() {{
            const cidTerm = document.getElementById('cidSearch').value.trim().toUpperCase();
            const aliasTerm = document.getElementById('aliasSearch').value.trim().toUpperCase();
            const mgrTerm = document.getElementById('mgrSearch').value.trim().toUpperCase();
            const teamTerm = document.getElementById('teamSearch').value.trim().toUpperCase();
            
            if (cidTerm === '' && aliasTerm === '' && mgrTerm === '' && teamTerm === '') {{
                renderTable(DATA.cids);
            }} else {{
                const filtered = DATA.cids.filter(cid => {{
                    const cidMatch = cidTerm === '' || cid.cid.toUpperCase().includes(cidTerm);
                    const aliasMatch = aliasTerm === '' || cid.alias.toUpperCase().includes(aliasTerm);
                    const mgrMatch = mgrTerm === '' || cid.mgr.toUpperCase().includes(mgrTerm);
                    const teamMatch = teamTerm === '' || cid.team.toUpperCase().includes(teamTerm);
                    return cidMatch && aliasMatch && mgrMatch && teamMatch;
                }});
                renderTable(filtered);
            }}
        }}
        
        function resetFilter() {{
            document.getElementById('cidSearch').value = '';
            document.getElementById('aliasSearch').value = '';
            document.getElementById('mgrSearch').value = '';
            document.getElementById('teamSearch').value = '';
            renderTable(DATA.cids);
        }}
        
        // Initial render
        renderTable(DATA.cids);
    </script>
</body>
</html>"""
    
    with open(output_filename, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"✅ HTMLファイルを生成しました: {output_filename}")
    return output_filename


if __name__ == '__main__':
    try:
        sourcing_df, target_df, suppression_df, mapping_df, config = load_real_data()
        data = process_real_data(sourcing_df, target_df, suppression_df, mapping_df, config)
        output_file = generate_interactive_html(data)
        print()
        print("=" * 60)
        print("✨ 完了！")
        print("=" * 60)
        print()
        print(f"📁 生成されたファイル: {output_file}")
        print()
        print("📌 使い方:")
        print("  1. HTMLファイルをダブルクリック")
        print("  2. CID、Alias、Mgr、Teamでフィルター検索")
        print("  3. 黄色のセルをクリックして値を入力")
        print("  4. Projected OPSが自動計算されます")
        print()
    except Exception as e:
        print(f"❌ エラーが発生しました: {e}")
        import traceback
        traceback.print_exc()
