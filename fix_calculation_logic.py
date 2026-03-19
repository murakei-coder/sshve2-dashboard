"""
Fix SSHVE2 Dashboard Calculation Logic
Corrects Target OPS, Forecast OPS, and Projected OPS calculations
"""
import json
from datetime import datetime

print("=" * 80)
print("Fixing SSHVE2 Dashboard Calculation Logic")
print("=" * 80)

# Load data
json_file = 'sshve2_data_v2_20260318_203513.json'
print(f"\nLoading: {json_file}")

with open(json_file, 'r', encoding='utf-8') as f:
    data = json.load(f)

print(f"✅ {len(data['cids'])} MCIDs loaded")

# Get filter values
teams = sorted(set(c['team'] for c in data['cids'] if c['team']))
mgrs = sorted(set(c['mgr'] for c in data['cids'] if c['mgr']))
aliases = sorted(set(c['alias'] for c in data['cids'] if c['alias']))

team_opts = '\n'.join(f'<option value="{t}">{t}</option>' for t in teams)
mgr_opts = '\n'.join(f'<option value="{m}">{m}</option>' for m in mgrs)
alias_opts = '\n'.join(f'<option value="{a}">{a}</option>' for a in aliases)

all_data_js = json.dumps(data['cids'], ensure_ascii=False)
coef_js = json.dumps(data['coefficients'], ensure_ascii=False)

output = f'sshve2_fixed_calc_{datetime.now().strftime("%Y%m%d_%H%M%S")}.html'

print(f"✅ Generating: {output}")

# HTML with CORRECTED calculation logic
html = f'''<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>SSHVE2 Dashboard - Fixed Calculations</title>
<style>
* {{margin:0;padding:0;box-sizing:border-box}}
body {{font-family:'Segoe UI','Yu Gothic',sans-serif;background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);padding:20px}}
.container {{max-width:2200px;margin:0 auto;background:#fff;border-radius:15px;box-shadow:0 10px 40px rgba(0,0,0,0.2)}}
.header {{background:linear-gradient(135deg,#1e3c72 0%,#2a5298 100%);color:#fff;padding:30px 40px}}
.header h1 {{font-size:2em;margin-bottom:10px}}
.content {{padding:40px}}
.info-box {{background:linear-gradient(135deg,#d4edda 0%,#c3e6cb 100%);border-left:5px solid #28a745;padding:20px;margin-bottom:30px;border-radius:8px}}
.filter-section {{background:linear-gradient(135deg,#f8f9fa 0%,#e9ecef 100%);padding:30px;border-radius:12px;margin-bottom:30px}}
.filter-row {{display:flex;gap:20px;flex-wrap:wrap;margin-bottom:20px}}
.filter-group {{flex:1;min-width:200px}}
.filter-group label {{display:block;font-weight:700;margin-bottom:8px;font-size:0.9em;color:#2c3e50}}
.filter-group select,.filter-group input {{width:100%;padding:12px;border:2px solid #ddd;border-radius:8px;font-size:0.95em}}
.btn-row {{display:flex;gap:15px;flex-wrap:wrap}}
.btn {{background:linear-gradient(135deg,#1e3c72 0%,#2a5298 100%);color:#fff;border:none;padding:14px 30px;border-radius:8px;cursor:pointer;font-weight:700;font-size:1em;transition:all 0.3s}}
.btn:hover {{transform:translateY(-2px);box-shadow:0 6px 20px rgba(30,60,114,0.4)}}
.btn-secondary {{background:linear-gradient(135deg,#6c757d 0%,#5a6268 100%)}}
.btn-success {{background:linear-gradient(135deg,#28a745 0%,#218838 100%)}}
.bulk-section {{background:#e7f3ff;padding:25px;border-radius:12px;margin-bottom:25px;border:2px solid #1e3c72;display:none}}
.bulk-section h3 {{margin-bottom:15px;color:#1e3c72}}
.bulk-row {{display:flex;gap:15px;align-items:end;flex-wrap:wrap}}
.bulk-group {{flex:1;min-width:180px}}
.table-container {{overflow-x:auto;margin-top:25px;border-radius:12px}}
table {{width:100%;border-collapse:collapse;font-size:0.75em;background:#fff}}
thead {{background:linear-gradient(135deg,#1e3c72 0%,#2a5298 100%);color:#fff;position:sticky;top:0;z-index:10}}
thead th {{padding:10px 5px;text-align:center;font-weight:700;border-right:1px solid rgba(255,255,255,0.2);font-size:0.75em;white-space:nowrap}}
tbody td {{padding:7px 5px;text-align:right;border-bottom:1px solid #e9ecef;border-right:1px solid #e9ecef}}
tbody td:nth-child(-n+5) {{text-align:left;background:#f8f9fa;font-weight:600}}
tbody tr:hover {{background:#f1f3f5}}
.editable {{background:#fff9e6!important;cursor:pointer;font-weight:700}}
.editable:hover {{background:#fff3cd!important}}
.calculated {{background:linear-gradient(135deg,#e7f3ff 0%,#cfe7ff 100%)!important;font-weight:800}}
.positive {{color:#28a745;font-weight:700}}
.negative {{color:#dc3545;font-weight:700}}
.number {{font-family:'Consolas',monospace}}
.empty {{text-align:center;padding:60px 20px;color:#6c757d}}
.stats {{display:flex;gap:20px;margin-bottom:25px;flex-wrap:wrap}}
.stat-card {{flex:1;min-width:200px;background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);color:#fff;padding:20px;border-radius:12px}}
.stat-card h4 {{font-size:0.9em;opacity:0.9;margin-bottom:8px}}
.stat-card .value {{font-size:2em;font-weight:800}}
</style>
</head>
<body>
<div class="container">
<div class="header">
<h1>🎯 SSHVE2 Dashboard (Fixed Calculations)</h1>
<p>📊 {len(data['cids'])} MCIDs | 🔄 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
</div>
<div class="content">
<div class="info-box">
<strong>✅ 計算ロジック修正済み:</strong>
<p>• Target OPS = Σ(Target GMS × SSHVE1% × 係数)<br>
• Forecast OPS = Σ(Current GMS × SSHVE2% × 係数)<br>
• Projected OPS = Σ(Improved GMS × Improved SSHVE2% × 係数)<br>
• 改善幅がゼロの場合、Projected OPS = Forecast OPS</p>
</div>
<div class="filter-section">
<div class="filter-row">
<div class="filter-group"><label>🏢 Team</label><select id="teamFilter"><option value="">-- Select --</option>{team_opts}</select></div>
<div class="filter-group"><label>👤 Mgr</label><select id="mgrFilter"><option value="">-- Select --</option>{mgr_opts}</select></div>
<div class="filter-group"><label>👨‍💼 Alias</label><select id="aliasFilter"><option value="">-- Select --</option>{alias_opts}</select></div>
<div class="filter-group"><label>🔢 MCID</label><input type="text" id="mcidFilter" placeholder="Enter MCID"></div>
</div>
<div class="btn-row">
<button class="btn" onclick="filterData()">🔍 検索</button>
<button class="btn btn-secondary" onclick="resetFilter()">🔄 リセット</button>
<button class="btn btn-secondary" onclick="exportCSV()">📥 CSV出力</button>
</div>
</div>
<div class="bulk-section" id="bulkSection">
<h3>📝 一括入力</h3>
<div class="bulk-row">
<div class="bulk-group"><label>Sourcing改善幅</label><input type="number" id="bulkSourcing" placeholder="0" step="1"></div>
<div class="bulk-group"><label>Price Error削減率%</label><input type="number" id="bulkPriceError" placeholder="0" step="0.1"></div>
<div class="bulk-group"><label>その他Suppression削減率%</label><input type="number" id="bulkOtherSupp" placeholder="0" step="0.1"></div>
<div class="bulk-group"><button class="btn btn-success" onclick="applyBulk()">✅ 一括適用</button></div>
</div>
</div>
<div id="statsSection"></div>
<div id="resultsSection">
<div class="empty"><h3>📋 フィルターを選択してください</h3></div>
</div>
</div>
</div>
<script>
const ALL_DATA={all_data_js};
const COEF={coef_js};
const userInputs={{}};
function fmt(n){{return Math.round(n).toLocaleString('ja-JP')}}
function pct(n){{return n.toFixed(1)+'%'}}

// CORRECTED CALCULATION LOGIC
function calcProjectedOPS(cid,curGMS,tgtGMS,ss1,ss2){{
const inp=userInputs[cid]||{{}};
const srcImp=parseFloat(inp.sourcing||0);
const peRed=parseFloat(inp.priceErrorReduction||0);
const othRed=parseFloat(inp.otherSuppReduction||0);

// Improved GMS = Current GMS + Sourcing改善幅
const impGMS=curGMS+srcImp;

// Calculate improved SSHVE2 percentages
// When reducing Price Error by X%, that X% moves to "No suppression"
// Same for other categories (OOS, VRP Missing, Others)
const ss2NoSupp=ss2['No suppression']+(ss2['Price Error']*peRed/100)+(ss2['OOS']*othRed/100)+(ss2['VRP Missing']*othRed/100)+(ss2['Others']*othRed/100);
const ss2OOS=ss2['OOS']*(1-othRed/100);
const ss2VRP=ss2['VRP Missing']*(1-othRed/100);
const ss2PE=ss2['Price Error']*(1-peRed/100);
const ss2Oth=ss2['Others']*(1-othRed/100);

// Target OPS = Σ(Target GMS × SSHVE1% × coefficient)
const targetOPS=(tgtGMS*ss1['No suppression']/100*COEF['No suppression'])+
(tgtGMS*ss1['OOS']/100*COEF['OOS'])+
(tgtGMS*ss1['VRP Missing']/100*COEF['VRP Missing'])+
(tgtGMS*ss1['Price Error']/100*COEF['Price Error'])+
(tgtGMS*ss1['Others']/100*COEF['Others']);

// Forecast OPS = Σ(Current GMS × SSHVE2% × coefficient)
const forecastOPS=(curGMS*ss2['No suppression']/100*COEF['No suppression'])+
(curGMS*ss2['OOS']/100*COEF['OOS'])+
(curGMS*ss2['VRP Missing']/100*COEF['VRP Missing'])+
(curGMS*ss2['Price Error']/100*COEF['Price Error'])+
(curGMS*ss2['Others']/100*COEF['Others']);

// Projected OPS = Σ(Improved GMS × Improved SSHVE2% × coefficient)
const projOPS=(impGMS*ss2NoSupp/100*COEF['No suppression'])+
(impGMS*ss2OOS/100*COEF['OOS'])+
(impGMS*ss2VRP/100*COEF['VRP Missing'])+
(impGMS*ss2PE/100*COEF['Price Error'])+
(impGMS*ss2Oth/100*COEF['Others']);

// Suppression改善幅 = Projected OPS - Forecast OPS (from suppression improvements only)
const suppImpFromPE=(curGMS*ss2['Price Error']/100*peRed/100*COEF['Price Error']);
const suppImpFromOth=(curGMS*(ss2['OOS']+ss2['VRP Missing']+ss2['Others'])/100*othRed/100*((COEF['OOS']+COEF['VRP Missing']+COEF['Others'])/3));
const suppImp=suppImpFromPE+suppImpFromOth;

// Incremental OPS = Projected OPS - Forecast OPS
const incOPS=projOPS-forecastOPS;

// vs Target = Projected OPS - Target OPS
const vsTarget=projOPS-targetOPS;

return{{srcImp,suppImp,projOPS,targetOPS,forecastOPS,vsTarget,incOPS,achRate:(projOPS/targetOPS*100)}};
}}

function edit(cell,cid,field){{
const val=userInputs[cid]?.[field]||0;
const inp=document.createElement('input');
inp.type='number';inp.value=val;inp.step=field==='sourcing'?'1':'0.1';inp.min='0';
inp.style.cssText='width:100%;padding:5px;border:2px solid #1e3c72;border-radius:4px';
inp.onblur=()=>{{updateVal(cid,field,inp.value)}};
inp.onkeypress=e=>{{if(e.key==='Enter')inp.blur()}};
cell.innerHTML='';cell.appendChild(inp);inp.focus();inp.select();
}}

function updateVal(cid,field,val){{
if(!userInputs[cid])userInputs[cid]={{}};
userInputs[cid][field]=parseFloat(val)||0;
renderTable(window.currentPlans);
}}

function applyBulk(){{
const src=parseFloat(document.getElementById('bulkSourcing').value)||0;
const pe=parseFloat(document.getElementById('bulkPriceError').value)||0;
const oth=parseFloat(document.getElementById('bulkOtherSupp').value)||0;
if(!window.currentPlans||window.currentPlans.length===0){{alert('⚠️ データなし');return}}
window.currentPlans.forEach(p=>{{
if(!userInputs[p.cid])userInputs[p.cid]={{}};
userInputs[p.cid].sourcing=src;
userInputs[p.cid].priceErrorReduction=pe;
userInputs[p.cid].otherSuppReduction=oth;
}});
renderTable(window.currentPlans);
alert(`✅ ${{window.currentPlans.length}}件適用`);
}}

function renderStats(plans){{
const totCur=plans.reduce((s,p)=>s+p.current_gms,0);
const totTgt=plans.reduce((s,p)=>s+p.target_gms,0);
const gap=totTgt-totCur;
const ach=(totCur/totTgt*100).toFixed(1);
document.getElementById('statsSection').innerHTML=`
<div class="stats">
<div class="stat-card"><h4>📊 Total Current</h4><div class="value">${{fmt(totCur)}}</div></div>
<div class="stat-card"><h4>🎯 Total Target</h4><div class="value">${{fmt(totTgt)}}</div></div>
<div class="stat-card"><h4>📈 Gap</h4><div class="value ${{gap>=0?'positive':'negative'}}">${{fmt(gap)}}</div></div>
<div class="stat-card"><h4>✅ Achievement</h4><div class="value">${{ach}}%</div></div>
</div>`;
}}

function renderTable(plans){{
const cont=document.getElementById('resultsSection');
const bulk=document.getElementById('bulkSection');
if(plans.length===0){{
cont.innerHTML='<div class="empty"><h3>❌ データなし</h3></div>';
document.getElementById('statsSection').innerHTML='';
bulk.style.display='none';
return;
}}
window.currentPlans=plans;
renderStats(plans);
bulk.style.display='block';
let h='<div class="table-container"><table><thead><tr>';
h+='<th rowspan="2">CID</th><th rowspan="2">Merchant<br>Name</th><th rowspan="2">Alias</th><th rowspan="2">Mgr</th><th rowspan="2">Team</th>';
h+='<th colspan="3">Sourced GMS</th><th colspan="2">過去参加ASIN</th>';
h+='<th colspan="5">SSHVE1 Suppression</th><th colspan="5">SSHVE2 Suppression</th>';
h+='<th colspan="3">Promotion OPS</th>';
h+='<th rowspan="2">Sourcing<br>改善幅</th><th rowspan="2">Price Error<br>削減率%</th><th rowspan="2">その他Supp<br>削減率%</th>';
h+='<th rowspan="2">Suppression<br>改善幅</th><th rowspan="2">Projected<br>OPS</th><th rowspan="2">Incremental<br>OPS</th><th rowspan="2">vs Target</th></tr>';
h+='<tr><th>Act</th><th>vs Target</th><th>Target</th><th>SSHVE1</th><th>T365</th>';
h+='<th>No Supp</th><th>OOS</th><th>VRP</th><th>Price</th><th>Others</th>';
h+='<th>No Supp</th><th>OOS</th><th>VRP</th><th>Price</th><th>Others</th>';
h+='<th>Forecast</th><th>vs Target</th><th>Target</th></tr></thead><tbody>';
plans.forEach(p=>{{
const c=calcProjectedOPS(p.cid,p.current_gms,p.target_gms,p.sshve1_suppression,p.sshve2_suppression);
h+='<tr>';
h+=`<td>${{p.cid}}</td>`;
h+=`<td>${{p.alias||'-'}}</td>`;
h+=`<td>${{p.alias}}</td>`;
h+=`<td>${{p.mgr}}</td>`;
h+=`<td>${{p.team}}</td>`;
h+=`<td class="number">${{fmt(p.current_gms)}}</td>`;
h+=`<td class="number ${{p.gap<0?'positive':'negative'}}">${{fmt(-p.gap)}}</td>`;
h+=`<td class="number">${{fmt(p.target_gms)}}</td>`;
h+=`<td class="number">${{p.event_participation.sshve1_flag.asin_count}}</td>`;
h+=`<td class="number">${{p.event_participation.t365_flag.asin_count}}</td>`;
['No suppression','OOS','VRP Missing','Price Error','Others'].forEach(cat=>{{
h+=`<td class="number">${{pct(p.sshve1_suppression[cat])}}</td>`;
}});
['No suppression','OOS','VRP Missing','Price Error','Others'].forEach(cat=>{{
h+=`<td class="number">${{pct(p.sshve2_suppression[cat])}}</td>`;
}});
h+=`<td class="number">${{fmt(c.forecastOPS)}}</td>`;
h+=`<td class="number ${{(c.forecastOPS-c.targetOPS)>=0?'positive':'negative'}}">${{fmt(c.forecastOPS-c.targetOPS)}}</td>`;
h+=`<td class="number">${{fmt(c.targetOPS)}}</td>`;
h+=`<td class="number editable" onclick="edit(this,'${{p.cid}}','sourcing')">${{fmt(c.srcImp)}}</td>`;
h+=`<td class="number editable" onclick="edit(this,'${{p.cid}}','priceErrorReduction')">${{pct(userInputs[p.cid]?.priceErrorReduction||0)}}</td>`;
h+=`<td class="number editable" onclick="edit(this,'${{p.cid}}','otherSuppReduction')">${{pct(userInputs[p.cid]?.otherSuppReduction||0)}}</td>`;
h+=`<td class="number calculated">${{fmt(c.suppImp)}}</td>`;
h+=`<td class="number calculated ${{c.achRate>=100?'positive':'negative'}}">${{fmt(c.projOPS)}}</td>`;
h+=`<td class="number calculated">${{fmt(c.incOPS)}}</td>`;
h+=`<td class="number calculated ${{c.vsTarget>=0?'positive':'negative'}}">${{fmt(c.vsTarget)}}</td>`;
h+='</tr>';
}});
h+='</tbody></table></div>';
cont.innerHTML=h;
}}

function filterData(){{
const team=document.getElementById('teamFilter').value;
const mgr=document.getElementById('mgrFilter').value;
const alias=document.getElementById('aliasFilter').value;
const mcid=document.getElementById('mcidFilter').value.trim();
if(!team&&!mgr&&!alias&&!mcid){{alert('⚠️ フィルター選択');return}}
const filtered=ALL_DATA.filter(c=>{{
if(team&&c.team!==team)return false;
if(mgr&&c.mgr!==mgr)return false;
if(alias&&c.alias!==alias)return false;
if(mcid&&!c.cid.includes(mcid))return false;
return true;
}});
renderTable(filtered);
}}

function resetFilter(){{
document.getElementById('teamFilter').value='';
document.getElementById('mgrFilter').value='';
document.getElementById('aliasFilter').value='';
document.getElementById('mcidFilter').value='';
document.getElementById('resultsSection').innerHTML='<div class="empty"><h3>📋 フィルター選択</h3></div>';
document.getElementById('statsSection').innerHTML='';
document.getElementById('bulkSection').style.display='none';
}}

function exportCSV(){{
if(!window.currentPlans||window.currentPlans.length===0){{alert('⚠️ データなし');return}}
const headers=['CID','Merchant Name','Alias','Mgr','Team','Current GMS','vs Target','Target GMS',
'SSHVE1 ASINs','T365 ASINs','SS1 No Supp%','SS1 OOS%','SS1 VRP%','SS1 Price%','SS1 Others%',
'SS2 No Supp%','SS2 OOS%','SS2 VRP%','SS2 Price%','SS2 Others%',
'Forecast OPS','vs Target OPS','Target OPS','Sourcing Imp','Price Error Red%','Other Supp Red%',
'Suppression Imp','Projected OPS','Incremental OPS','vs Target'];
let csv=headers.join(',')+`\\n`;
window.currentPlans.forEach(p=>{{
const c=calcProjectedOPS(p.cid,p.current_gms,p.target_gms,p.sshve1_suppression,p.sshve2_suppression);
const row=[p.cid,p.alias||'-',p.alias,p.mgr,p.team,p.current_gms,-p.gap,p.target_gms,
p.event_participation.sshve1_flag.asin_count,p.event_participation.t365_flag.asin_count,
p.sshve1_suppression['No suppression'],p.sshve1_suppression['OOS'],p.sshve1_suppression['VRP Missing'],
p.sshve1_suppression['Price Error'],p.sshve1_suppression['Others'],
p.sshve2_suppression['No suppression'],p.sshve2_suppression['OOS'],p.sshve2_suppression['VRP Missing'],
p.sshve2_suppression['Price Error'],p.sshve2_suppression['Others'],
c.forecastOPS,c.forecastOPS-c.targetOPS,c.targetOPS,c.srcImp,
userInputs[p.cid]?.priceErrorReduction||0,userInputs[p.cid]?.otherSuppReduction||0,
c.suppImp,c.projOPS,c.incOPS,c.vsTarget];
csv+=row.join(',')+`\\n`;
}});
const blob=new Blob([csv],{{type:'text/csv;charset=utf-8;'}});
const link=document.createElement('a');
link.href=URL.createObjectURL(blob);
link.download=`sshve2_fixed_${{new Date().toISOString().slice(0,10)}}.csv`;
link.click();
}}
</script>
</body>
</html>''';

with open(output, 'w', encoding='utf-8') as f:
    f.write(html)

print(f"\n✅ Created: {output}")
print(f"📊 Size: {len(html)/1024:.2f} KB")
print("\n" + "=" * 80)
print("✨ 修正内容:")
print("  ✅ Target OPS = Σ(Target GMS × SSHVE1% × 係数)")
print("  ✅ Forecast OPS = Σ(Current GMS × SSHVE2% × 係数)")
print("  ✅ Projected OPS = Σ(Improved GMS × Improved SSHVE2% × 係数)")
print("  ✅ 改善幅ゼロ時: Projected OPS = Forecast OPS")
print("  ✅ 係数一貫性確保")
print("=" * 80)
