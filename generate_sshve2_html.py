import json
from datetime import datetime

# Load data
with open("sshve2_data_20260318_181018.json", "r", encoding="utf-8") as f:
    data = json.load(f)

print(f"Loaded {len(data['cids'])} MCIDs")

# Get unique filter values
teams = sorted(set(c["team"] for c in data["cids"] if c["team"]))
mgrs = sorted(set(c["mgr"] for c in data["cids"] if c["mgr"]))
aliases = sorted(set(c["alias"] for c in data["cids"] if c["alias"]))

print(f"Teams: {len(teams)}, Mgrs: {len(mgrs)}, Aliases: {len(aliases)}")

output_file = f"sshve2_dashboard_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"

html = f"""<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SSHVE2 Bridge Plan Dashboard</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: 'Segoe UI', sans-serif; background: #f5f7fa; padding: 20px; }}
        .container {{ max-width: 1900px; margin: 0 auto; background: white; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        .header {{ background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%); color: white; padding: 25px 30px; }}
        .header h1 {{ font-size: 1.8em; margin-bottom: 5px; }}
        .content {{ padding: 30px; }}
        .info-box {{ background: #fff3cd; border-left: 4px solid #ffc107; padding: 15px; margin-bottom: 20px; border-radius: 5px; }}
        .filter-section {{ background: #f8f9fa; padding: 20px; border-radius: 8px; margin-bottom: 25px; border-left: 4px solid #1e3c72; }}
        .filter-row {{ display: flex; gap: 15px; align-items: flex-end; flex-wrap: wrap; }}
        .filter-group {{ flex: 1; min-width: 200px; }}
        .filter-group label {{ display: block; font-weight: 600; margin-bottom: 5px; color: #333; font-size: 0.9em; }}
        .filter-group input, .filter-group select {{ width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 5px; font-size: 0.95em; }}
        .btn {{ background: #1e3c72; color: white; border: none; padding: 10px 25px; border-radius: 5px; cursor: pointer; font-weight: 600; }}
        .btn:hover {{ background: #2a5298; }}
        .btn-secondary {{ background: #6c757d; }}
        .btn-secondary:hover {{ background: #5a6268; }}
        .table-container {{ overflow-x: auto; margin-top: 20px; }}
        table {{ width: 100%; border-collapse: collapse; font-size: 0.85em; }}
        thead {{ background: #1e3c72; color: white; }}
        thead th {{ padding: 12px 6px; text-align: center; font-weight: 600; border-right: 1px solid rgba(255,255,255,0.2); font-size: 0.8em; white-space: nowrap; }}
        tbody td {{ padding: 8px 6px; text-align: right; border-bottom: 1px solid #e9ecef; border-right: 1px solid #e9ecef; font-size: 0.9em; }}
        tbody td:first-child, tbody td:nth-child(2), tbody td:nth-child(3), tbody td:nth-child(4) {{ text-align: left; background: #f8f9fa; font-weight: 500; }}
        tbody tr:hover {{ background: #f8f9fa; }}
        .editable-cell {{ background: #fff9e6 !important; cursor: pointer; font-weight: 600; }}
        .editable-cell:hover {{ background: #fff3cd !important; }}
        .calculated-cell {{ background: #e7f3ff !important; font-weight: 700; }}
        .positive {{ color: #28a745; font-weight: 600; }}
        .negative {{ color: #dc3545; font-weight: 600; }}
        .number {{ font-family: 'Consolas', monospace; }}
        .pct {{ font-size: 0.8em; color: #666; }}
        .empty-state {{ text-align: center; padding: 40px; color: #666; }}
        .result-count {{ margin: 15px 0; font-weight: 600; color: #1e3c72; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1> SSHVE2 Bridge Plan Dashboard</h1>
            <p>Total MCIDs: {len(data['cids'])} | Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>
        <div class="content">
            <div class="info-box">
                <strong> 使い方:</strong> フィルターを使用してMCIDを検索してください。黄色のセルをクリックして値を入力すると、Projected OPSが自動計算されます。
            </div>
            <div class="filter-section">
                <div class="filter-row">
                    <div class="filter-group">
                        <label>MCID</label>
                        <input type="text" id="cidSearch" placeholder="MCIDを入力">
                    </div>
                    <div class="filter-group">
                        <label>Alias</label>
                        <select id="aliasSearch">
                            <option value="">-- Select Alias --</option>
                            {''.join(f'<option value="{a}">{a}</option>' for a in aliases)}
                        </select>
                    </div>
                    <div class="filter-group">
                        <label>Mgr</label>
                        <select id="mgrSearch">
                            <option value="">-- Select Mgr --</option>
                            {''.join(f'<option value="{m}">{m}</option>' for m in mgrs)}
                        </select>
                    </div>
                    <div class="filter-group">
                        <label>Team</label>
                        <select id="teamSearch">
                            <option value="">-- Select Team --</option>
                            {''.join(f'<option value="{t}">{t}</option>' for t in teams)}
                        </select>
                    </div>
                    <button class="btn" onclick="filterData()"> 検索</button>
                    <button class="btn btn-secondary" onclick="resetFilter()"> リセット</button>
                </div>
            </div>
            <div class="result-count" id="resultCount"></div>
            <div class="table-container">
                <table>
                    <thead>
                        <tr>
                            <th rowspan="2">MCID</th>
                            <th rowspan="2">Alias</th>
                            <th rowspan="2">Mgr</th>
                            <th rowspan="2">Team</th>
                            <th colspan="2">Sourced GMS</th>
                            <th colspan="2">過去参加ASIN</th>
                            <th colspan="5">Suppression Rate</th>
                            <th colspan="2">Promotion OPS</th>
                            <th rowspan="2">Sourcing<br>改善幅</th>
                            <th rowspan="2">Price Error<br>削減率%</th>
                            <th rowspan="2">Projected<br>OPS</th>
                        </tr>
                        <tr>
                            <th>Act</th>
                            <th>vs Target</th>
                            <th>SS HVE1</th>
                            <th>T365</th>
                            <th>No Supp</th>
                            <th>OOS</th>
                            <th>VRP Miss</th>
                            <th>Price Err</th>
                            <th>Others</th>
                            <th>Forecast</th>
                            <th>vs Target</th>
                        </tr>
                    </thead>
                    <tbody id="tableBody">
                        <tr><td colspan="20" class="empty-state">フィルターを使用してMCIDを検索してください</td></tr>
                    </tbody>
                </table>
            </div>
        </div>
    </div>
    <script>
        const DATA = {json.dumps(data, ensure_ascii=False)};
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
                sourcingImprovement,
                suppressionImprovement,
                projectedOPS,
                vsTarget: projectedOPS - targetGMS,
                achievementRate: (projectedOPS / targetGMS * 100)
            }};
        }}
        
        function makeEditable(cell, cid, field) {{
            const currentValue = userInputs[cid]?.[field] || 0;
            cell.innerHTML = `<input type="number" value="${{currentValue}}" onblur="updateValue('${{cid}}', '${{field}}', this.value)" onkeypress="if(event.key==='Enter') this.blur()" step="0.01" min="0">`;
            cell.querySelector('input').focus();
            cell.querySelector('input').select();
        }}
        
        function updateValue(cid, field, value) {{
            if (!userInputs[cid]) userInputs[cid] = {{}};
            userInputs[cid][field] = parseFloat(value) || 0;
            renderTable(window.currentPlans);
        }}
        
        function renderTable(plans) {{
            const tbody = document.getElementById('tableBody');
            tbody.innerHTML = '';
            window.currentPlans = plans;
            
            if (plans.length === 0) {{
                tbody.innerHTML = '<tr><td colspan="20" class="empty-state">検索結果がありません</td></tr>';
                document.getElementById('resultCount').textContent = '';
                return;
            }}
            
            document.getElementById('resultCount').textContent = `検索結果: ${{plans.length}} MCIDs`;
            
            plans.forEach(plan => {{
                const row = document.createElement('tr');
                const calc = calculateProjectedOPS(plan.cid, plan.current_gms, plan.target_gms, plan.suppression_breakdown);
                
                // MCID, Alias, Mgr, Team
                ['cid', 'alias', 'mgr', 'team'].forEach(field => {{
                    const cell = document.createElement('td');
                    cell.textContent = plan[field];
                    row.appendChild(cell);
                }});
                
                // Current GMS
                const actCell = document.createElement('td');
                actCell.className = 'number';
                actCell.textContent = formatNumber(plan.current_gms);
                row.appendChild(actCell);
                
                // vs Target
                const vsTargetCell = document.createElement('td');
                vsTargetCell.className = 'number ' + (plan.gap < 0 ? 'positive' : 'negative');
                vsTargetCell.innerHTML = `${{formatNumber(-plan.gap)}}<br><span class="pct">${{formatPercent(-plan.gap / plan.target_gms * 100)}}</span>`;
                row.appendChild(vsTargetCell);
                
                // Event participation
                ['sshve1_flag', 't365_flag'].forEach(flag => {{
                    const cell = document.createElement('td');
                    cell.className = 'number';
                    cell.textContent = plan.event_participation[flag].asin_count;
                    row.appendChild(cell);
                }});
                
                // Suppression rates
                ['No suppression', 'OOS', 'VRP Missing', 'Price Error', 'Others'].forEach(cat => {{
                    const cell = document.createElement('td');
                    cell.className = 'number';
                    cell.textContent = formatPercent(plan.suppression_breakdown[cat].percentage);
                    row.appendChild(cell);
                }});
                
                // Forecast
                const forecastCell = document.createElement('td');
                forecastCell.className = 'number';
                forecastCell.textContent = formatNumber(plan.target_gms);
                row.appendChild(forecastCell);
                
                // vs Target (projected)
                const projVsTargetCell = document.createElement('td');
                projVsTargetCell.className = 'number ' + (calc.vsTarget >= 0 ? 'positive' : 'negative');
                projVsTargetCell.textContent = formatNumber(calc.vsTarget);
                row.appendChild(projVsTargetCell);
                
                // Sourcing improvement (editable)
                const sourcingCell = document.createElement('td');
                sourcingCell.className = 'number editable-cell';
                sourcingCell.textContent = formatNumber(calc.sourcingImprovement);
                sourcingCell.onclick = function() {{ makeEditable(this, plan.cid, 'sourcing'); }};
                row.appendChild(sourcingCell);
                
                // Price error reduction (editable)
                const priceErrorReduction = userInputs[plan.cid]?.priceErrorReduction || 0;
                const priceErrorCell = document.createElement('td');
                priceErrorCell.className = 'number editable-cell';
                priceErrorCell.textContent = formatPercent(priceErrorReduction);
                priceErrorCell.onclick = function() {{ makeEditable(this, plan.cid, 'priceErrorReduction'); }};
                row.appendChild(priceErrorCell);
                
                // Projected OPS (calculated)
                const projectedCell = document.createElement('td');
                projectedCell.className = 'number calculated-cell ' + (calc.achievementRate >= 100 ? 'positive' : 'negative');
                projectedCell.innerHTML = `${{formatNumber(calc.projectedOPS)}}<br><span class="pct">${{formatPercent(calc.achievementRate)}}</span>`;
                row.appendChild(projectedCell);
                
                tbody.appendChild(row);
            }});
        }}
        
        function filterData() {{
            const cidTerm = document.getElementById('cidSearch').value.trim().toUpperCase();
            const aliasTerm = document.getElementById('aliasSearch').value;
            const mgrTerm = document.getElementById('mgrSearch').value;
            const teamTerm = document.getElementById('teamSearch').value;
            
            if (!cidTerm && !aliasTerm && !mgrTerm && !teamTerm) {{
                alert('少なくとも1つのフィルターを選択してください');
                return;
            }}
            
            const filtered = DATA.cids.filter(cid => {{
                const cidMatch = !cidTerm || cid.cid.toUpperCase().includes(cidTerm);
                const aliasMatch = !aliasTerm || cid.alias === aliasTerm;
                const mgrMatch = !mgrTerm || cid.mgr === mgrTerm;
                const teamMatch = !teamTerm || cid.team === teamTerm;
                return cidMatch && aliasMatch && mgrMatch && teamMatch;
            }});
            
            renderTable(filtered);
        }}
        
        function resetFilter() {{
            document.getElementById('cidSearch').value = '';
            document.getElementById('aliasSearch').value = '';
            document.getElementById('mgrSearch').value = '';
            document.getElementById('teamSearch').value = '';
            document.getElementById('tableBody').innerHTML = '<tr><td colspan="20" class="empty-state">フィルターを使用してMCIDを検索してください</td></tr>';
            document.getElementById('resultCount').textContent = '';
        }}
    </script>
</body>
</html>"""

with open(output_file, "w", encoding="utf-8") as f:
    f.write(html)

print(f"Generated {output_file}")
