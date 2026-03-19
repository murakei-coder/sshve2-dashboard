"""
Create Fixed SSHVE2 Dashboard with:
1. SSHVE1 Suppression rate columns
2. SSHVE2 Suppression rate columns (properly displayed)
3. Team/Mgr bulk input functionality
"""

import json
from datetime import datetime

print("=" * 70)
print("Creating Fixed SSHVE2 Dashboard...")
print("=" * 70)

# Load the real data (not mock)
json_file = 'sshve2_data_v2_20260318_203513.json'
print(f"\nLoading data from {json_file}...")

with open(json_file, 'r', encoding='utf-8') as f:
    data = json.load(f)

print(f"✅ Loaded {len(data['cids'])} MCIDs")

# Get unique filter values
teams = sorted(set(c['team'] for c in data['cids'] if c['team']))
mgrs = sorted(set(c['mgr'] for c in data['cids'] if c['mgr']))
aliases = sorted(set(c['alias'] for c in data['cids'] if c['alias']))

print(f"Teams: {len(teams)}, Mgrs: {len(mgrs)}, Aliases: {len(aliases)}")

# Create filter options
team_options = '\n'.join(f'                            <option value="{t}">{t}</option>' for t in teams)
mgr_options = '\n'.join(f'                            <option value="{m}">{m}</option>' for m in mgrs)
alias_options = '\n'.join(f'                            <option value="{a}">{a}</option>' for a in aliases)

# Embed data as JavaScript
all_data_js = json.dumps(data['cids'], ensure_ascii=False, indent=2)
coefficients_js = json.dumps(data['coefficients'], ensure_ascii=False)

html_content = f'''<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SSHVE2 Bridge Plan Dashboard - Fixed Version</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ 
            font-family: 'Segoe UI', 'Yu Gothic', 'Meiryo', sans-serif; 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            min-height: 100vh;
        }}
        .container {{ 
            max-width: 2000px; 
            margin: 0 auto; 
            background: white; 
            border-radius: 15px; 
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
            overflow: hidden;
        }}
        .header {{ 
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%); 
            color: white; 
            padding: 30px 40px;
        }}
        .header h1 {{ font-size: 2.2em; margin-bottom: 10px; }}
        .header p {{ font-size: 1.1em; opacity: 0.9; }}
        .content {{ padding: 40px; }}
        .info-box {{ 
            background: linear-gradient(135deg, #fff3cd 0%, #ffe69c 100%);
            border-left: 5px solid #ffc107; 
            padding: 20px; 
            margin-bottom: 30px; 
            border-radius: 8px;
        }}
        .filter-section {{ 
            background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
            padding: 30px; 
            border-radius: 12px; 
            margin-bottom: 30px;
        }}
        .filter-row {{ display: flex; gap: 20px; flex-wrap: wrap; margin-bottom: 20px; }}
        .filter-group {{ flex: 1; min-width: 220px; }}
        .filter-group label {{ display: block; font-weight: 700; margin-bottom: 8px; font-size: 0.95em; color: #2c3e50; }}
        .filter-group select, .filter-group input {{ 
            width: 100%; padding: 12px; border: 2px solid #ddd; border-radius: 8px;
            font-size: 0.95em; transition: all 0.3s ease;
        }}
        .filter-group select:focus, .filter-group input:focus {{
            outline: none; border-color: #1e3c72; box-shadow: 0 0 0 3px rgba(30, 60, 114, 0.1);
        }}
        .btn-row {{ display: flex; gap: 15px; flex-wrap: wrap; }}
        .btn {{ 
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            color: white; border: none; padding: 14px 30px; border-radius: 8px; 
            cursor: pointer; font-weight: 700; font-size: 1em;
            transition: all 0.3s ease; box-shadow: 0 4px 15px rgba(30, 60, 114, 0.3);
        }}
        .btn:hover {{ transform: translateY(-2px); box-shadow: 0 6px 20px rgba(30, 60, 114, 0.4); }}
        .btn-secondary {{ background: linear-gradient(135deg, #6c757d 0%, #5a6268 100%); }}
        .btn-success {{ background: linear-gradient(135deg, #28a745 0%, #218838 100%); }}
        .bulk-input-section {{
            background: #e7f3ff;
            padding: 25px;
            border-radius: 12px;
            margin-bottom: 25px;
            border: 2px solid #1e3c72;
        }}
        .bulk-input-section h3 {{ margin-bottom: 15px; color: #1e3c72; }}
        .bulk-input-row {{ display: flex; gap: 15px; align-items: end; flex-wrap: wrap; }}
        .bulk-input-group {{ flex: 1; min-width: 180px; }}
        .table-container {{ overflow-x: auto; margin-top: 25px; border-radius: 12px; }}
        table {{ width: 100%; border-collapse: collapse; font-size: 0.8em; background: white; }}
        thead {{ background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%); color: white; position: sticky; top: 0; z-index: 10; }}
        thead th {{ 
            padding: 12px 6px; text-align: center; font-weight: 700; 
            border-right: 1px solid rgba(255,255,255,0.2); 
            font-size: 0.8em; white-space: nowrap;
        }}
        tbody td {{ padding: 8px 6px; text-align: right; border-bottom: 1px solid #e9ecef; border-right: 1px solid #e9ecef; }}
        tbody td:nth-child(-n+4) {{ text-align: left; background: #f8f9fa; font-weight: 600; }}
        tbody tr:hover {{ background: #f1f3f5; }}
        .editable-cell {{ background: #fff9e6 !important; cursor: pointer; font-weight: 700; }}
        .editable-cell:hover {{ background: #fff3cd !important; }}
        .calculated-cell {{ background: linear-gradient(135deg, #e7f3ff 0%, #cfe7ff 100%) !important; font-weight: 800; }}
        .positive {{ color: #28a745; font-weight: 700; }}
        .negative {{ color: #dc3545; font-weight: 700; }}
        .number {{ font-family: 'Consolas', 'Monaco', monospace; }}
        .empty-state {{ text-align: center; padding: 60px 20px; color: #6c757d; }}
        .stats-row {{ display: flex; gap: 20px; margin-bottom: 25px; flex-wrap: wrap; }}
        .stat-card {{
            flex: 1; min-width: 200px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white; padding: 20px; border-radius: 12px;
        }}
        .stat-card h4 {{ font-size: 0.9em; opacity: 0.9; margin-bottom: 8px; }}
        .stat-card .value {{ font-size: 2em; font-weight: 800; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎯 SSHVE2 Bridge Plan Dashboard - Fixed Version</h1>
            <p>📊 Total MCIDs: {len(data['cids'])} | 🔄 Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>
        <div class="content">
            <div class="info-box">
                <strong>💡 使い方:</strong>
                <p>1. Team/Mgr/Alias/MCIDでフィルタリング<br>
                2. 黄色のセルをクリックして個別入力、または下の一括入力機能を使用<br>
                3. SSHVE1とSSHVE2のSuppression rateが両方表示されます</p>
            </div>
            
            <div class="filter-section">
                <div class="filter-row">
                    <div class="filter-group">
                        <label>🏢 Team</label>
                        <select id="teamFilter">
                            <option value="">-- Select Team --</option>
{team_options}
                        </select>
                    </div>
                    <div class="filter-group">
                        <label>👤 Manager</label>
                        <select id="mgrFilter">
                            <option value="">-- Select Mgr --</option>
{mgr_options}
                        </select>
                    </div>
                    <div class="filter-group">
                        <label>👨‍💼 Alias</label>
                        <select id="aliasFilter">
                            <option value="">-- Select Alias --</option>
{alias_options}
                        </select>
                    </div>
                    <div class="filter-group">
                        <label>🔢 MCID</label>
                        <input type="text" id="mcidFilter" placeholder="Enter MCID">
                    </div>
                </div>
                <div class="btn-row">
                    <button class="btn" onclick="filterData()">🔍 検索</button>
                    <button class="btn btn-secondary" onclick="resetFilter()">🔄 リセット</button>
                    <button class="btn btn-secondary" onclick="exportToCSV()">📥 CSV出力</button>
                </div>
            </div>
            
            <div class="bulk-input-section" id="bulkInputSection" style="display:none;">
                <h3>📝 一括入力 (表示中の全MCIDに適用)</h3>
                <div class="bulk-input-row">
                    <div class="bulk-input-group">
                        <label>Sourcing改善幅</label>
                        <input type="number" id="bulkSourcing" placeholder="0" step="1">
                    </div>
                    <div class="bulk-input-group">
                        <label>Price Error削減率 (%)</label>
                        <input type="number" id="bulkPriceError" placeholder="0" step="0.1">
                    </div>
                    <div class="bulk-input-group">
                        <button class="btn btn-success" onclick="applyBulkInput()">✅ 一括適用</button>
                    </div>
                </div>
            </div>
            
            <div id="statsSection"></div>
            <div id="resultsSection">
                <div class="empty-state">
                    <h3>📋 フィルターを選択してください</h3>
                    <p>Team、Mgr、Alias、またはMCIDを選択して検索ボタンをクリックしてください</p>
                </div>
            </div>
        </div>
    </div>
    
    <script>
        const ALL_DATA = {all_data_js};
        const COEFFICIENTS = {coefficients_js};
        const userInputs = {{}};
        
        function formatNumber(num) {{ return Math.round(num).toLocaleString('ja-JP'); }}
        function formatPercent(num) {{ return num.toFixed(1) + '%'; }}
        
        function calculateProjectedOPS(cid, currentGMS, targetGMS, sshve2Supp) {{
            const inputs = userInputs[cid] || {{}};
            const sourcingImprovement = parseFloat(inputs.sourcing || 0);
            const priceErrorReduction = parseFloat(inputs.priceErrorReduction || 0);
            const currentPriceErrorPct = sshve2Supp['Price Error'] / 100;
            const suppressionImprovement = currentGMS * currentPriceErrorPct * (priceErrorReduction / 100) * COEFFICIENTS['Price Error'];
            const projectedOPS = currentGMS + sourcingImprovement + suppressionImprovement;
            
            return {{
                sourcingImprovement, suppressionImprovement, projectedOPS,
                vsTarget: projectedOPS - targetGMS,
                achievementRate: (projectedOPS / targetGMS * 100)
            }};
        }}
        
        function makeEditable(cell, cid, field) {{
            const currentValue = userInputs[cid]?.[field] || 0;
            const input = document.createElement('input');
            input.type = 'number';
            input.value = currentValue;
            input.step = field === 'priceErrorReduction' ? '0.1' : '1';
            input.min = '0';
            input.style.width = '100%';
            input.style.padding = '5px';
            input.style.border = '2px solid #1e3c72';
            input.style.borderRadius = '4px';
            
            input.onblur = function() {{ updateValue(cid, field, this.value); }};
            input.onkeypress = function(e) {{ if(e.key === 'Enter') this.blur(); }};
            
            cell.innerHTML = '';
            cell.appendChild(input);
            input.focus();
            input.select();
        }}
        
        function updateValue(cid, field, value) {{
            if (!userInputs[cid]) userInputs[cid] = {{}};
            userInputs[cid][field] = parseFloat(value) || 0;
            renderTable(window.currentPlans);
        }}
        
        function applyBulkInput() {{
            const sourcing = parseFloat(document.getElementById('bulkSourcing').value) || 0;
            const priceError = parseFloat(document.getElementById('bulkPriceError').value) || 0;
            
            if (!window.currentPlans || window.currentPlans.length === 0) {{
                alert('⚠️ データがありません');
                return;
            }}
            
            window.currentPlans.forEach(plan => {{
                if (!userInputs[plan.cid]) userInputs[plan.cid] = {{}};
                userInputs[plan.cid].sourcing = sourcing;
                userInputs[plan.cid].priceErrorReduction = priceError;
            }});
            
            renderTable(window.currentPlans);
            alert(`✅ ${{window.currentPlans.length}}件のMCIDに一括適用しました`);
        }}
        
        function renderStats(plans) {{
            const totalCurrent = plans.reduce((sum, p) => sum + p.current_gms, 0);
            const totalTarget = plans.reduce((sum, p) => sum + p.target_gms, 0);
            const totalGap = totalTarget - totalCurrent;
            const avgAchievement = (totalCurrent / totalTarget * 100).toFixed(1);
            
            const html = `
                <div class="stats-row">
                    <div class="stat-card">
                        <h4>📊 Total Current GMS</h4>
                        <div class="value">${{formatNumber(totalCurrent)}}</div>
                    </div>
                    <div class="stat-card">
                        <h4>🎯 Total Target GMS</h4>
                        <div class="value">${{formatNumber(totalTarget)}}</div>
                    </div>
                    <div class="stat-card">
                        <h4>📈 Gap</h4>
                        <div class="value ${{totalGap >= 0 ? 'positive' : 'negative'}}">${{formatNumber(totalGap)}}</div>
                    </div>
                    <div class="stat-card">
                        <h4>✅ Achievement Rate</h4>
                        <div class="value">${{avgAchievement}}%</div>
                    </div>
                </div>
            `;
            document.getElementById('statsSection').innerHTML = html;
        }}
        
        function renderTable(plans) {{
            const container = document.getElementById('resultsSection');
            const bulkSection = document.getElementById('bulkInputSection');
            
            if (plans.length === 0) {{
                container.innerHTML = '<div class="empty-state"><h3>❌ 該当するデータがありません</h3></div>';
                document.getElementById('statsSection').innerHTML = '';
                bulkSection.style.display = 'none';
                return;
            }}
            
            window.currentPlans = plans;
            renderStats(plans);
            bulkSection.style.display = 'block';
            
            let html = '<div class="table-container"><table><thead><tr>';
            html += '<th rowspan="2">MCID</th><th rowspan="2">Alias</th><th rowspan="2">Mgr</th><th rowspan="2">Team</th>';
            html += '<th colspan="2">Sourced GMS</th><th colspan="2">過去参加ASIN</th>';
            html += '<th colspan="5">SSHVE1 Suppression</th>';
            html += '<th colspan="5">SSHVE2 Suppression</th>';
            html += '<th colspan="2">Promotion OPS</th>';
            html += '<th rowspan="2">Sourcing<br>改善幅</th><th rowspan="2">Price Error<br>削減率%</th><th rowspan="2">Projected<br>OPS</th></tr>';
            html += '<tr><th>Current</th><th>vs Target</th><th>SSHVE1</th><th>T365</th>';
            html += '<th>No Supp</th><th>OOS</th><th>VRP</th><th>Price</th><th>Others</th>';
            html += '<th>No Supp</th><th>OOS</th><th>VRP</th><th>Price</th><th>Others</th>';
            html += '<th>Forecast</th><th>vs Target</th></tr></thead><tbody>';
            
            plans.forEach(plan => {{
                const calc = calculateProjectedOPS(plan.cid, plan.current_gms, plan.target_gms, plan.sshve2_suppression);
                html += '<tr>';
                html += `<td>${{plan.cid}}</td><td>${{plan.alias}}</td><td>${{plan.mgr}}</td><td>${{plan.team}}</td>`;
                html += `<td class="number">${{formatNumber(plan.current_gms)}}</td>`;
                html += `<td class="number ${{plan.gap < 0 ? 'positive' : 'negative'}}">${{formatNumber(-plan.gap)}}</td>`;
                html += `<td class="number">${{plan.event_participation.sshve1_flag.asin_count}}</td>`;
                html += `<td class="number">${{plan.event_participation.t365_flag.asin_count}}</td>`;
                
                // SSHVE1 Suppression
                ['No suppression', 'OOS', 'VRP Missing', 'Price Error', 'Others'].forEach(cat => {{
                    html += `<td class="number">${{formatPercent(plan.sshve1_suppression[cat])}}</td>`;
                }});
                
                // SSHVE2 Suppression
                ['No suppression', 'OOS', 'VRP Missing', 'Price Error', 'Others'].forEach(cat => {{
                    html += `<td class="number">${{formatPercent(plan.sshve2_suppression[cat])}}</td>`;
                }});
                
                html += `<td class="number">${{formatNumber(plan.forecast_ops)}}</td>`;
                html += `<td class="number ${{plan.vs_target_ops >= 0 ? 'positive' : 'negative'}}">${{formatNumber(plan.vs_target_ops)}}</td>`;
                html += `<td class="number editable-cell" onclick="makeEditable(this, '${{plan.cid}}', 'sourcing')">${{formatNumber(calc.sourcingImprovement)}}</td>`;
                html += `<td class="number editable-cell" onclick="makeEditable(this, '${{plan.cid}}', 'priceErrorReduction')">${{formatPercent(userInputs[plan.cid]?.priceErrorReduction || 0)}}</td>`;
                html += `<td class="number calculated-cell ${{calc.achievementRate >= 100 ? 'positive' : 'negative'}}">${{formatNumber(calc.projectedOPS)}}</td>`;
                html += '</tr>';
            }});
            
            html += '</tbody></table></div>';
            container.innerHTML = html;
        }}
        
        function filterData() {{
            const team = document.getElementById('teamFilter').value;
            const mgr = document.getElementById('mgrFilter').value;
            const alias = document.getElementById('aliasFilter').value;
            const mcid = document.getElementById('mcidFilter').value.trim();
            
            if (!team && !mgr && !alias && !mcid) {{
                alert('⚠️ フィルターを1つ以上選択してください');
                return;
            }}
            
            const filtered = ALL_DATA.filter(c => {{
                if (team && c.team !== team) return false;
                if (mgr && c.mgr !== mgr) return false;
                if (alias && c.alias !== alias) return false;
                if (mcid && !c.cid.includes(mcid)) return false;
                return true;
            }});
            
            renderTable(filtered);
        }}
        
        function resetFilter() {{
            document.getElementById('teamFilter').value = '';
            document.getElementById('mgrFilter').value = '';
            document.getElementById('aliasFilter').value = '';
            document.getElementById('mcidFilter').value = '';
            document.getElementById('resultsSection').innerHTML = '<div class="empty-state"><h3>📋 フィルターを選択してください</h3></div>';
            document.getElementById('statsSection').innerHTML = '';
            document.getElementById('bulkInputSection').style.display = 'none';
        }}
        
        function exportToCSV() {{
            if (!window.currentPlans || window.currentPlans.length === 0) {{
                alert('⚠️ データがありません');
                return;
            }}
            
            const headers = ['MCID', 'Alias', 'Mgr', 'Team', 'Current GMS', 'Target GMS', 'Gap',
                           'SSHVE1 ASINs', 'T365 ASINs',
                           'SS1 No Supp%', 'SS1 OOS%', 'SS1 VRP%', 'SS1 Price%', 'SS1 Others%',
                           'SS2 No Supp%', 'SS2 OOS%', 'SS2 VRP%', 'SS2 Price%', 'SS2 Others%',
                           'Forecast OPS', 'vs Target OPS', 'Sourcing Improvement', 'Price Error Reduction%', 'Projected OPS'];
            
            let csv = headers.join(',') + '\\n';
            
            window.currentPlans.forEach(plan => {{
                const calc = calculateProjectedOPS(plan.cid, plan.current_gms, plan.target_gms, plan.sshve2_suppression);
                const row = [
                    plan.cid, plan.alias, plan.mgr, plan.team,
                    plan.current_gms, plan.target_gms, plan.gap,
                    plan.event_participation.sshve1_flag.asin_count,
                    plan.event_participation.t365_flag.asin_count,
                    plan.sshve1_suppression['No suppression'],
                    plan.sshve1_suppression['OOS'],
                    plan.sshve1_suppression['VRP Missing'],
                    plan.sshve1_suppression['Price Error'],
                    plan.sshve1_suppression['Others'],
                    plan.sshve2_suppression['No suppression'],
                    plan.sshve2_suppression['OOS'],
                    plan.sshve2_suppression['VRP Missing'],
                    plan.sshve2_suppression['Price Error'],
                    plan.sshve2_suppression['Others'],
                    plan.forecast_ops, plan.vs_target_ops,
                    calc.sourcingImprovement,
                    userInputs[plan.cid]?.priceErrorReduction || 0,
                    calc.projectedOPS
                ];
                csv += row.join(',') + '\\n';
            }});
            
            const blob = new Blob([csv], {{ type: 'text/csv;charset=utf-8;' }});
            const link = document.createElement('a');
            link.href = URL.createObjectURL(blob);
            link.download = `sshve2_bridge_plan_${{new Date().toISOString().slice(0,10)}}.csv`;
            link.click();
        }}
    </script>
</body>
</html>'''

# Save the fixed HTML file
output_file = f'sshve2_dashboard_fixed_{datetime.now().strftime("%Y%m%d_%H%M%S")}.html'
with open(output_file, 'w', encoding='utf-8') as f:
    f.write(html_content)

print(f"\n✅ Created fixed HTML dashboard: {output_file}")
print(f"📊 File size: {len(html_content) / 1024:.2f} KB")
print("\n" + "=" * 70)
print("✨ Done! All issues fixed:")
print("  ✅ SSHVE1 Suppression rate columns added")
print("  ✅ SSHVE2 Suppression rate properly displayed")
print("  ✅ Team/Mgr bulk input functionality added")
print("=" * 70)
