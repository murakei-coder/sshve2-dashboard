import json
from datetime import datetime

# Load the JSON data
with open('sshve2_data_20260318_181018.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

print(f'Loaded {len(data["cids"])} MCIDs')

# Get unique filter values
teams = sorted(set(c['team'] for c in data['cids'] if c['team']))
mgrs = sorted(set(c['mgr'] for c in data['cids'] if c['mgr']))
aliases = sorted(set(c['alias'] for c in data['cids'] if c['alias']))

print(f'Teams: {len(teams)}, Mgrs: {len(mgrs)}, Aliases: {len(aliases)}')

# Create team options
team_options = '\n'.join(f'                            <option value="{t}">{t}</option>' for t in teams)
mgr_options = '\n'.join(f'                            <option value="{m}">{m}</option>' for m in mgrs)
alias_options = '\n'.join(f'                            <option value="{a}">{a}</option>' for a in aliases)

# Generate HTML
html_template = '''<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <title>SSHVE2 Bridge Plan Dashboard</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: 'Segoe UI', 'Yu Gothic', sans-serif; background: #f5f7fa; padding: 20px; }}
        .container {{ max-width: 1900px; margin: 0 auto; background: white; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        .header {{ background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%); color: white; padding: 25px 30px; }}
        .header h1 {{ font-size: 1.8em; margin-bottom: 5px; }}
        .content {{ padding: 30px; }}
        .info-box {{ background: #fff3cd; border-left: 4px solid #ffc107; padding: 15px; margin-bottom: 20px; border-radius: 5px; }}
        .filter-section {{ background: #f8f9fa; padding: 20px; border-radius: 8px; margin-bottom: 25px; }}
        .filter-row {{ display: flex; gap: 15px; flex-wrap: wrap; margin-bottom: 15px; }}
        .filter-group {{ flex: 1; min-width: 200px; }}
        .filter-group label {{ display: block; font-weight: 600; margin-bottom: 5px; font-size: 0.9em; }}
        .filter-group select, .filter-group input {{ width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 5px; }}
        .btn {{ background: #1e3c72; color: white; border: none; padding: 10px 25px; border-radius: 5px; cursor: pointer; font-weight: 600; }}
        .btn:hover {{ background: #2a5298; }}
        .btn-secondary {{ background: #6c757d; }}
        .table-container {{ overflow-x: auto; margin-top: 20px; }}
        table {{ width: 100%; border-collapse: collapse; font-size: 0.85em; }}
        thead {{ background: #1e3c72; color: white; }}
        thead th {{ padding: 12px 6px; text-align: center; font-weight: 600; border-right: 1px solid rgba(255,255,255,0.2); font-size: 0.8em; white-space: nowrap; }}
        tbody td {{ padding: 8px 6px; text-align: right; border-bottom: 1px solid #e9ecef; border-right: 1px solid #e9ecef; }}
        tbody td:nth-child(-n+4) {{ text-align: left; background: #f8f9fa; font-weight: 500; }}
        tbody tr:hover {{ background: #f8f9fa; }}
        .editable-cell {{ background: #fff9e6 !important; cursor: pointer; font-weight: 600; }}
        .editable-cell:hover {{ background: #fff3cd !important; }}
        .calculated-cell {{ background: #e7f3ff !important; font-weight: 700; }}
        .positive {{ color: #28a745; font-weight: 600; }}
        .negative {{ color: #dc3545; font-weight: 600; }}
        .number {{ font-family: 'Consolas', monospace; }}
        .empty-state {{ text-align: center; padding: 40px; color: #666; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎯 SSHVE2 Bridge Plan Dashboard</h1>
            <p>Total MCIDs: {total_mcids}</p>
        </div>
        <div class="content">
            <div class="info-box">
                <strong>💡 使い方:</strong> Team/Mgr/Aliasのいずれかを選択してから「検索」ボタンをクリックしてください
            </div>
            <div class="filter-section">
                <div class="filter-row">
                    <div class="filter-group">
                        <label>Team</label>
                        <select id="teamFilter">
                            <option value="">-- Select Team --</option>
{team_options}
                        </select>
                    </div>
                    <div class="filter-group">
                        <label>Mgr</label>
                        <select id="mgrFilter">
                            <option value="">-- Select Mgr --</option>
{mgr_options}
                        </select>
                    </div>
                    <div class="filter-group">
                        <label>Alias</label>
                        <select id="aliasFilter">
                            <option value="">-- Select Alias --</option>
{alias_options}
                        </select>
                    </div>
                    <div class="filter-group">
                        <label>MCID</label>
                        <input type="text" id="mcidFilter" placeholder="Enter MCID">
                    </div>
                </div>
                <div class="filter-row">
                    <button class="btn" onclick="filterData()">🔍 検索</button>
                    <button class="btn btn-secondary" onclick="resetFilter()">🔄 リセット</button>
                </div>
            </div>
            <div id="resultsSection">
                <div class="empty-state">
                    <h3>フィルターを選択してください</h3>
                    <p>Team、Mgr、Alias、またはMCIDを選択して検索ボタンをクリックしてください</p>
                </div>
            </div>
        </div>
    </div>
    <script>
        const ALL_DATA = {all_data_json};
        const COEFFICIENTS = {{"Price Error": 0.275}};
        const userInputs = {{}};
        
        function formatNumber(num) {{ return Math.round(num).toLocaleString('ja-JP'); }}
        function formatPercent(num) {{ return num.toFixed(1) + '%'; }}
        
        function calculateProjectedOPS(cid, currentGMS, targetGMS, suppBreakdown) {{
            const inputs = userInputs[cid] || {{}};
            const sourcingImprovement = parseFloat(inputs.sourcing || 0);
            const priceErrorReduction = parseFloat(inputs.priceErrorReduction || 0);
            const currentPriceErrorPct = suppBreakdown['Price Error'].percentage / 100;
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
            input.step = '0.01';
            input.min = '0';
            input.onblur = function() {{ updateValue(cid, field, this.value); }};
            input.onkeypress = function(e) {{ if(e.key === 'Enter') this.blur(); }};
            cell.innerHTML = '';
            cell.appendChild(input);
            input.focus();
        }}
        
        function updateValue(cid, field, value) {{
            if (!userInputs[cid]) userInputs[cid] = {{}};
            userInputs[cid][field] = parseFloat(value) || 0;
            renderTable(window.currentPlans);
        }}
        
        function renderTable(plans) {{
            const container = document.getElementById('resultsSection');
            if (plans.length === 0) {{
                container.innerHTML = '<div class="empty-state"><h3>該当するデータがありません</h3></div>';
                return;
            }}
            
            window.currentPlans = plans;
            let html = '<div class="table-container"><table><thead><tr>';
            html += '<th rowspan="2">MCID</th><th rowspan="2">Alias</th><th rowspan="2">Mgr</th><th rowspan="2">Team</th>';
            html += '<th colspan="2">Sourced GMS</th><th colspan="2">過去参加ASIN</th><th colspan="5">Suppression Rate</th>';
            html += '<th colspan="2">Promotion OPS</th><th rowspan="2">Sourcing改善幅</th><th rowspan="2">Price Error削減率%</th><th rowspan="2">Projected OPS</th></tr>';
            html += '<tr><th>Act</th><th>vs Target</th><th>SS HVE1</th><th>T365</th>';
            html += '<th>No Supp</th><th>OOS</th><th>VRP Miss</th><th>Price Err</th><th>Others</th>';
            html += '<th>Forecast</th><th>vs Target</th></tr></thead><tbody>';
            
            plans.forEach(plan => {{
                const calc = calculateProjectedOPS(plan.cid, plan.current_gms, plan.target_gms, plan.suppression_breakdown);
                html += '<tr>';
                html += `<td>${{plan.cid}}</td><td>${{plan.alias}}</td><td>${{plan.mgr}}</td><td>${{plan.team}}</td>`;
                html += `<td class="number">${{formatNumber(plan.current_gms)}}</td>`;
                html += `<td class="number ${{plan.gap < 0 ? 'positive' : 'negative'}}">${{formatNumber(-plan.gap)}}</td>`;
                html += `<td class="number">${{plan.event_participation.sshve1_flag.asin_count}}</td>`;
                html += `<td class="number">${{plan.event_participation.t365_flag.asin_count}}</td>`;
                ['No suppression', 'OOS', 'VRP Missing', 'Price Error', 'Others'].forEach(cat => {{
                    html += `<td class="number">${{formatPercent(plan.suppression_breakdown[cat].percentage)}}</td>`;
                }});
                html += `<td class="number">${{formatNumber(plan.target_gms)}}</td>`;
                html += `<td class="number ${{calc.vsTarget >= 0 ? 'positive' : 'negative'}}">${{formatNumber(calc.vsTarget)}}</td>`;
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
                alert('フィルターを1つ以上選択してください');
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
            document.getElementById('resultsSection').innerHTML = '<div class="empty-state"><h3>フィルターを選択してください</h3></div>';
        }}
    </script>
</body>
</html>'''

html = html_template.format(
    total_mcids=len(data['cids']),
    team_options=team_options,
    mgr_options=mgr_options,
    alias_options=alias_options,
    all_data_json=json.dumps(data['cids'], ensure_ascii=False)
)

output_file = 'sshve2_dashboard_' + datetime.now().strftime('%Y%m%d_%H%M%S') + '.html'
with open(output_file, 'w', encoding='utf-8') as f:
    f.write(html)

print(f'✅ Created {output_file}')
print('Done!')
