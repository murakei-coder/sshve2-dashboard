"""
Generate SSHVE2 Dashboard V3 - Enhanced Version
- OOS and VRP Missing coefficients set to 0
- Cascading filter hierarchy: Team > Mgr > Alias > MCID = Merchant Name
- Optimized: Pre-aggregated suppression data (reduced file size from 145MB to ~5MB)
- CSV export with UTF-8 BOM (fixes character encoding issues)
- QuickSight link for raw data access
- Seller action summary (Sourcing/Suppression focus recommendations)
- Team summary statistics
- Clear unit labels for improvement inputs (金額 vs %)
"""
import json
import pandas as pd
from datetime import datetime

print("=" * 80)
print("Generating SSHVE2 Dashboard V2 - Zero OOS/VRP Coef + Cascading Filters")
print("=" * 80)

# Load corrected data
json_file = 'sshve2_data_new_suppression_20260318_222020.json'
print(f"\nLoading: {json_file}")

with open(json_file, 'r', encoding='utf-8') as f:
    data = json.load(f)

print(f"✅ {len(data['cids'])} MCIDs loaded")

# Load raw suppression data and pre-aggregate by MCID
suppression_file = r'C:\Users\murakei\Desktop\SSHVE2\Dashboard\raw\Suppression\SSHVE2_ByASIN_Suppression_raw_Final.txt'
print(f"\nLoading raw suppression data: {suppression_file}")
df_suppression = pd.read_csv(suppression_file, sep='\t', encoding='utf-8')
print(f"✅ Loaded {len(df_suppression):,} rows")

# Pre-aggregate by MCID: sum OPS by category
suppression_by_mcid = {}
for mcid, group in df_suppression.groupby('merchant_customer_id'):
    mcid_str = str(mcid)
    # Aggregate: sum OPS for each category
    category_ops = {}
    for _, row in group.iterrows():
        cat = row['suppression_category_large']
        ops = float(row['t30d_ops']) if pd.notna(row['t30d_ops']) else 0
        category_ops[cat] = category_ops.get(cat, 0) + ops
    
    # Store aggregated data
    suppression_by_mcid[mcid_str] = category_ops

print(f"✅ Pre-aggregated suppression data for {len(suppression_by_mcid)} MCIDs")

# Override coefficients: Set OOS and VRP Missing to 0
data['coefficients']['OOS'] = 0
data['coefficients']['VRP Missing'] = 0

print(f"✅ Coefficients updated: OOS=0, VRP Missing=0")

# Calculate average SSHVE1 suppression percentages across all CE sellers
# This will be used as fallback for sellers with all-zero SSHVE1 suppression
print(f"\n📊 Calculating average SSHVE1 suppression across all CE sellers...")
sshve1_totals = {'No suppression': 0, 'OOS': 0, 'VRP Missing': 0, 'Price Error': 0, 'Others': 0}
sshve1_count = 0

for cid_data in data['cids']:
    ss1 = cid_data['sshve1_suppression']
    # Check if this seller has non-zero SSHVE1 data
    total = sum(ss1.values())
    if total > 0:
        for cat in sshve1_totals.keys():
            sshve1_totals[cat] += ss1[cat]
        sshve1_count += 1

# Calculate average percentages
if sshve1_count > 0:
    sshve1_avg = {cat: sshve1_totals[cat] / sshve1_count for cat in sshve1_totals.keys()}
else:
    # Fallback to equal distribution if no data
    sshve1_avg = {'No suppression': 20, 'OOS': 20, 'VRP Missing': 20, 'Price Error': 20, 'Others': 20}

print(f"✅ Average SSHVE1 suppression calculated from {sshve1_count} sellers:")
for cat, val in sshve1_avg.items():
    print(f"   {cat}: {val:.2f}%")

# Apply fallback to sellers with all-zero SSHVE1 suppression
fallback_count = 0
for cid_data in data['cids']:
    ss1 = cid_data['sshve1_suppression']
    total = sum(ss1.values())
    if total == 0 and cid_data['target_gms'] > 0:
        # Apply average suppression percentages
        cid_data['sshve1_suppression'] = sshve1_avg.copy()
        cid_data['sshve1_suppression_fallback'] = True  # Mark as using fallback
        fallback_count += 1
    else:
        cid_data['sshve1_suppression_fallback'] = False

print(f"✅ Applied fallback SSHVE1 suppression to {fallback_count} sellers with all-zero data")

# Store average for JavaScript
data['sshve1_avg'] = sshve1_avg

# Get filter values
teams = sorted(set(c['team'] for c in data['cids'] if c['team']))
mgrs = sorted(set(c['mgr'] for c in data['cids'] if c['mgr']))
aliases = sorted(set(c['alias'] for c in data['cids'] if c['alias']))
merchants = sorted(set(str(c['merchant_name']) for c in data['cids'] if c['merchant_name'] and c['merchant_name'] != 'nan'))

team_opts = '\n'.join(f'<option value="{t}">{t}</option>' for t in teams)
mgr_opts = '\n'.join(f'<option value="{m}">{m}</option>' for m in mgrs)
alias_opts = '\n'.join(f'<option value="{a}">{a}</option>' for a in aliases)
merchant_opts = '\n'.join(f'<option value="{m}">{m}</option>' for m in merchants)

all_data_js = json.dumps(data['cids'], ensure_ascii=False)
coef_js = json.dumps(data['coefficients'], ensure_ascii=False)
suppression_data_js = json.dumps(suppression_by_mcid, ensure_ascii=False)
sshve1_avg_js = json.dumps(data['sshve1_avg'], ensure_ascii=False)

# Note: Raw data is too large to embed in HTML (would make file >100MB)
# Users can access raw data via QuickSight link
print(f"✅ Skipping raw data embedding (file size optimization)")

output = f'sshve2_dashboard_v3_enhanced_{datetime.now().strftime("%Y%m%d_%H%M%S")}.html'

print(f"✅ Generating: {output}")

# HTML with GMS-weighted no suppression rate calculation
html = f'''<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>SSHVE2 Opportunity Dashboard</title>
<style>
* {{margin:0;padding:0;box-sizing:border-box}}
body {{font-family:'Segoe UI','Yu Gothic',sans-serif;background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);padding:20px}}
.container {{max-width:2200px;margin:0 auto;background:#fff;border-radius:15px;box-shadow:0 10px 40px rgba(0,0,0,0.2)}}
.header {{background:linear-gradient(135deg,#1e3c72 0%,#2a5298 100%);color:#fff;padding:30px 40px}}
.header h1 {{font-size:2em;margin-bottom:10px}}
.content {{padding:40px}}
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
thead th {{padding:10px 5px;text-align:center;font-weight:700;border-right:1px solid rgba(255,255,255,0.2);font-size:0.75em;white-space:nowrap;cursor:pointer;user-select:none}}
thead th:hover {{background:rgba(255,255,255,0.1)}}
.sort-indicator {{margin-left:5px;font-size:0.8em;opacity:0.7}}
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
<h1>🎯 SSHVE2 Opportunity Dashboard</h1>
<p id="headerInfo">📊 {len(data['cids'])} MCIDs (Total) | 🔄 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
</div>
<div class="content">
<div style="background:linear-gradient(135deg,#4CAF50 0%,#45a049 100%);padding:20px;margin-bottom:25px;border-radius:12px;text-align:center;box-shadow:0 4px 15px rgba(0,0,0,0.2)">
<a href="https://us-east-1.quicksight.aws.amazon.com/sn/account/amazonbi/dashboards/863e3abc-b6f2-421d-9b11-dee511261bad/sheets/863e3abc-b6f2-421d-9b11-dee511261bad_d274b393-3f0a-4573-bab8-a67d87d50ec9" target="_blank" style="color:#fff;text-decoration:none;font-size:1.3em;font-weight:700;display:block">
📊 QuickSight - ASIN単位のRawデータを確認
</a>
<p style="color:#fff;margin-top:8px;font-size:0.9em;opacity:0.95">クリックしてASIN別の詳細データを表示</p>
</div>
<div style="background:linear-gradient(135deg,#fff3e0 0%,#ffe0b2 100%);border-left:5px solid #FF9800;padding:20px;margin-bottom:25px;border-radius:8px">
<h3 style="color:#E65100;margin-bottom:15px">📊 Suppression Category 係数</h3>
<div style="display:grid;grid-template-columns:repeat(5,1fr);gap:15px">
<div style="text-align:center">
<div style="font-weight:700;color:#4CAF50;font-size:1.1em">No suppression</div>
<div style="font-size:1.3em;font-family:Consolas,monospace;margin-top:5px">0.5343</div>
</div>
<div style="text-align:center">
<div style="font-weight:700;color:#2196F3;font-size:1.1em">OOS</div>
<div style="font-size:1.3em;font-family:Consolas,monospace;margin-top:5px;color:#999">0.0000</div>
</div>
<div style="text-align:center">
<div style="font-weight:700;color:#9C27B0;font-size:1.1em">VRP Missing</div>
<div style="font-size:1.3em;font-family:Consolas,monospace;margin-top:5px;color:#999">0.0000</div>
</div>
<div style="text-align:center">
<div style="font-weight:700;color:#F44336;font-size:1.1em">Price Error</div>
<div style="font-size:1.3em;font-family:Consolas,monospace;margin-top:5px">0.2750</div>
</div>
<div style="text-align:center">
<div style="font-weight:700;color:#FF9800;font-size:1.1em">Others</div>
<div style="font-size:1.3em;font-family:Consolas,monospace;margin-top:5px">0.1801</div>
</div>
</div>
</div>
<div style="background:linear-gradient(135deg,#e3f2fd 0%,#bbdefb 100%);border-left:5px solid #2196F3;padding:20px;margin-bottom:25px;border-radius:8px">
<h3 style="color:#1565C0;margin-bottom:15px">📖 指標の説明</h3>
<div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:20px;margin-bottom:15px">
<div>
<strong style="color:#2196F3">Forecast OPS</strong>
<p style="margin:5px 0 0 0;font-size:0.9em">現在のGMSとSSHVE2 Suppressionから算出される予測OPS</p>
<p style="margin:5px 0 0 0;font-size:0.8em;color:#666;font-family:Consolas,monospace">Σ(Current GMS × SSHVE2% × 係数)</p>
</div>
<div>
<strong style="color:#FFC107">Target OPS</strong>
<p style="margin:5px 0 0 0;font-size:0.9em">Target GMSとSSHVE1 Suppressionから算出される目標OPS</p>
<p style="margin:5px 0 0 0;font-size:0.8em;color:#666;font-family:Consolas,monospace">Σ(Target GMS × SSHVE1% × 係数)</p>
<p style="margin:5px 0 0 0;font-size:0.75em;color:#FF6B6B;font-style:italic">※SS HVE1 SuppressionデータがないセラーはPF平均の数字を使用（灰色ハイライト）</p>
</div>
<div>
<strong style="color:#9C27B0">Projected OPS</strong>
<p style="margin:5px 0 0 0;font-size:0.9em">改善施策（Sourcing、Suppression削減）を適用した後の予測OPS</p>
<p style="margin:5px 0 0 0;font-size:0.8em;color:#666;font-family:Consolas,monospace">Σ(Improved GMS × Improved SSHVE2% × 係数)</p>
</div>
</div>
<h3 style="color:#1565C0;margin:20px 0 10px 0">💡 使い方</h3>
<ol style="margin:0;padding-left:20px;font-size:0.9em">
<li>Team/Mgr/Alias/MCIDでフィルターをかけて対象を絞り込む</li>
<li>上部のQuickSightリンクまたはCIDをクリックしてASIN単位のRawデータを確認可能</li>
<li>Action Focusカラムで各セラーの推奨アクション（Sourcing/Suppression/Both/Maintain）を確認</li>
<li>黄色のセル（Sourcing改善幅、削減率）をクリックして数値を入力
  <ul style="margin-top:5px">
    <li><strong>Sourcing改善幅</strong>: 金額で入力（例: 10000 → 1万円の改善）</li>
    <li><strong>OOS改善率</strong>: %の数値のみ入力（例: 20 → 20%改善、5.5 → 5.5%改善）</li>
    <li><strong>Price Error削減率</strong>: %の数値のみ入力（例: 15 → 15%削減）</li>
    <li><strong>その他Suppression削減率</strong>: %の数値のみ入力（例: 10 → 10%削減）</li>
  </ul>
</li>
<li>一括入力機能で複数のMCIDに同じ値を適用可能</li>
<li>Projected OPSとIncremental OPSが自動計算される</li>
<li>CSV出力で結果をダウンロード可能</li>
</ol>
</div>
<div class="filter-section">
<div class="filter-row">
<div class="filter-group"><label>🏢 Team</label><select id="teamFilter" onchange="updateCascadingFilters()"><option value="">-- Select --</option>{team_opts}</select></div>
<div class="filter-group"><label>👤 Mgr</label><select id="mgrFilter" onchange="updateCascadingFilters()"><option value="">-- Select --</option>{mgr_opts}</select></div>
<div class="filter-group"><label>👨‍💼 Alias</label><select id="aliasFilter" onchange="updateCascadingFilters()"><option value="">-- Select --</option>{alias_opts}</select></div>
<div class="filter-group"><label>🔢 MCID</label><input type="text" id="mcidFilter" placeholder="Enter MCID"></div>
<div class="filter-group"><label>🏪 Merchant Name</label><select id="merchantFilter"><option value="">-- Select --</option>{merchant_opts}</select></div>
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
<div class="bulk-group"><label>Sourcing改善幅 (金額)</label><input type="number" id="bulkSourcing" placeholder="例: 10000" step="1"></div>
<div class="bulk-group"><label>OOS改善率 (%)</label><input type="number" id="bulkOOS" placeholder="例: 20 (=20%)" step="0.1"></div>
<div class="bulk-group"><label>Price Error削減率 (%)</label><input type="number" id="bulkPriceError" placeholder="例: 15 (=15%)" step="0.1"></div>
<div class="bulk-group"><label>その他Suppression削減率 (%)</label><input type="number" id="bulkOtherSupp" placeholder="例: 10 (=10%)" step="0.1"></div>
<div class="bulk-group"><button class="btn btn-success" onclick="applyBulk()">✅ 一括適用</button></div>
</div>
</div>
<div id="statsSection"></div>
<div id="teamSummarySection"></div>
<div id="summarySection" style="display:none;margin-bottom:30px">
<div style="display:grid;grid-template-columns:1fr 1fr;gap:30px">
<div style="background:#fff;padding:25px;border-radius:12px;box-shadow:0 4px 15px rgba(0,0,0,0.1)">
<h3 style="margin-bottom:20px;color:#1e3c72;text-align:center">📊 Forecast vs Target</h3>
<table style="width:100%;border-collapse:collapse">
<thead style="background:#f8f9fa">
<tr>
<th style="padding:12px;text-align:left;border-bottom:2px solid #dee2e6">指標</th>
<th style="padding:12px;text-align:right;border-bottom:2px solid #dee2e6">値</th>
</tr>
</thead>
<tbody>
<tr>
<td style="padding:12px;border-bottom:1px solid #dee2e6">Forecast OPS</td>
<td id="forecastOPS" style="padding:12px;text-align:right;border-bottom:1px solid #dee2e6;font-family:Consolas,monospace;font-weight:700;color:#2196F3">-</td>
</tr>
<tr>
<td style="padding:12px;border-bottom:1px solid #dee2e6">Target OPS</td>
<td id="targetOPS1" style="padding:12px;text-align:right;border-bottom:1px solid #dee2e6;font-family:Consolas,monospace;font-weight:700;color:#FFC107">-</td>
</tr>
<tr>
<td style="padding:12px">vs Target</td>
<td id="forecastVsTarget" style="padding:12px;text-align:right;font-family:Consolas,monospace;font-weight:700">-</td>
</tr>
</tbody>
</table>
</div>
<div style="background:#fff;padding:25px;border-radius:12px;box-shadow:0 4px 15px rgba(0,0,0,0.1)">
<h3 style="margin-bottom:20px;color:#1e3c72;text-align:center">🎯 Projected vs Target</h3>
<table style="width:100%;border-collapse:collapse">
<thead style="background:#f8f9fa">
<tr>
<th style="padding:12px;text-align:left;border-bottom:2px solid #dee2e6">指標</th>
<th style="padding:12px;text-align:right;border-bottom:2px solid #dee2e6">値</th>
</tr>
</thead>
<tbody>
<tr>
<td style="padding:12px;border-bottom:1px solid #dee2e6">Projected OPS</td>
<td id="projectedOPS" style="padding:12px;text-align:right;border-bottom:1px solid #dee2e6;font-family:Consolas,monospace;font-weight:700;color:#9C27B0">-</td>
</tr>
<tr>
<td style="padding:12px;border-bottom:1px solid #dee2e6">Target OPS</td>
<td id="targetOPS2" style="padding:12px;text-align:right;border-bottom:1px solid #dee2e6;font-family:Consolas,monospace;font-weight:700;color:#FFC107">-</td>
</tr>
<tr>
<td style="padding:12px">vs Target</td>
<td id="projectedVsTarget" style="padding:12px;text-align:right;font-family:Consolas,monospace;font-weight:700">-</td>
</tr>
</tbody>
</table>
</div>
</div>
</div>
<div id="resultsSection">
<div class="empty"><h3>📋 フィルターを選択してください</h3></div>
</div>
</div>
</div>
<script>
const ALL_DATA={all_data_js};
const COEF={coef_js};
const SUPPRESSION_DATA={suppression_data_js};
const SSHVE1_AVG={sshve1_avg_js};  // Average SSHVE1 suppression across all CE sellers
const userInputs={{}};
let currentSortColumn=null;
let currentSortDirection='asc';
function fmt(n){{return Math.round(n).toLocaleString('ja-JP')}}
function pct(n){{return n.toFixed(1)+'%'}}

// Calculate GMS-weighted no suppression rate from aggregated data
function calcWeightedNoSuppRate(plans){{
const mcids=plans.map(p=>p.cid);
let totalOPS=0;
let noSuppOPS=0;
mcids.forEach(cid=>{{
const suppData=SUPPRESSION_DATA[cid];
if(suppData){{
// suppData is now aggregated: {{category: totalOPS}}
Object.keys(suppData).forEach(cat=>{{
const ops=suppData[cat]||0;
totalOPS+=ops;
if(cat==='1.no suppression'){{
noSuppOPS+=ops;
}}
}});
}}
}});
return totalOPS>0?(noSuppOPS/totalOPS*100):0;
}}

// CORRECTED CALCULATION LOGIC
// Note: For sellers with all-zero SSHVE1 suppression but non-zero Target GMS,
// the average SSHVE1 suppression across all CE sellers is used as fallback.
// This ensures Target OPS can be calculated even when individual seller data is missing.
function calcProjectedOPS(cid,curGMS,tgtGMS,ss1,ss2){{
const inp=userInputs[cid]||{{}};
const srcImp=parseFloat(inp.sourcing||0);
const oosRed=parseFloat(inp.oosImprovement||0);
const peRed=parseFloat(inp.priceErrorReduction||0);
const othRed=parseFloat(inp.otherSuppReduction||0);

// Improved GMS = Current GMS + Sourcing改善幅
const impGMS=curGMS+srcImp;

// Calculate improved SSHVE2 percentages
// OOS improvement: OOS% reduced by oosRed%, added to No suppression
const ss2NoSupp=ss2['No suppression']+(ss2['OOS']*oosRed/100)+(ss2['Price Error']*peRed/100)+(ss2['VRP Missing']*othRed/100)+(ss2['Others']*othRed/100);
const ss2OOS=ss2['OOS']*(1-oosRed/100);
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

// Suppression改善幅
const suppImp=projOPS-forecastOPS-srcImp*COEF['No suppression'];

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
renderTableContent(window.currentPlans);
renderStats(window.currentPlans);
}}

function applyBulk(){{
const src=parseFloat(document.getElementById('bulkSourcing').value)||0;
const oos=parseFloat(document.getElementById('bulkOOS').value)||0;
const pe=parseFloat(document.getElementById('bulkPriceError').value)||0;
const oth=parseFloat(document.getElementById('bulkOtherSupp').value)||0;
if(!window.currentPlans||window.currentPlans.length===0){{alert('⚠️ データなし');return}}
window.currentPlans.forEach(p=>{{
if(!userInputs[p.cid])userInputs[p.cid]={{}};
userInputs[p.cid].sourcing=src;
userInputs[p.cid].oosImprovement=oos;
userInputs[p.cid].priceErrorReduction=pe;
userInputs[p.cid].otherSuppReduction=oth;
}});
renderTableContent(window.currentPlans);
renderStats(window.currentPlans);
alert(`✅ ${{window.currentPlans.length}}件適用`);
}}

function renderStats(plans){{
// Update header with filtered count
const totalMCIDs={len(data['cids'])};
const filteredCount=plans.length;
document.getElementById('headerInfo').innerHTML=`📊 ${{filteredCount}} MCIDs (Total: ${{totalMCIDs}}) | 🔄 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}`;

const totCur=plans.reduce((s,p)=>s+p.current_gms,0);
const totTgt=plans.reduce((s,p)=>s+p.target_gms,0);
const gap=totCur-totTgt;

// Calculate GMS-weighted no suppression rate from aggregated data (SSHVE2)
const noSuppRate=calcWeightedNoSuppRate(plans);

// Calculate SSHVE1 no suppression rate (weighted by target GMS)
let sshve1NoSuppTotal=0;
let sshve1TotalWeight=0;
plans.forEach(p=>{{
if(p.target_gms>0){{
sshve1NoSuppTotal+=p.sshve1_suppression['No suppression']*p.target_gms;
sshve1TotalWeight+=p.target_gms;
}}
}});
const sshve1NoSuppRate=sshve1TotalWeight>0?(sshve1NoSuppTotal/sshve1TotalWeight):0;
const vsSSHVE1=noSuppRate-sshve1NoSuppRate;

// Calculate total Forecast OPS and Projected OPS
let totalForecastOPS=0;
let totalTargetOPS=0;
let totalProjectedOPS=0;
plans.forEach(p=>{{
const c=calcProjectedOPS(p.cid,p.current_gms,p.target_gms,p.sshve1_suppression,p.sshve2_suppression);
totalForecastOPS+=c.forecastOPS;
totalTargetOPS+=c.targetOPS;
totalProjectedOPS+=c.projOPS;
}});

document.getElementById('statsSection').innerHTML=`
<div class="stats">
<div class="stat-card"><h4>📊 Sourced T30 GMS</h4><div class="value">${{fmt(totCur)}}</div></div>
<div class="stat-card"><h4>🎯 Target T30 GMS</h4><div class="value">${{fmt(totTgt)}}</div></div>
<div class="stat-card"><h4>📈 Gap</h4><div class="value ${{gap>=0?'positive':'negative'}}">${{fmt(gap)}}</div></div>
<div class="stat-card"><h4>✅ No Suppression Rate</h4><div class="value">${{pct(noSuppRate)}}</div><div style="font-size:0.7em;margin-top:5px;opacity:0.9">vs SSHVE1: <span class="${{vsSSHVE1>=0?'positive':'negative'}}">${{vsSSHVE1>=0?'+':''}}${{vsSSHVE1.toFixed(1)}}%</span></div></div>
</div>`;

// Render team summary
renderTeamSummary(plans);

// Render summary tables
renderSummaryTables(totalForecastOPS,totalProjectedOPS,totalTargetOPS);
}}

function renderTeamSummary(plans){{
// Determine grouping level based on current filter
const team=document.getElementById('teamFilter').value;
const mgr=document.getElementById('mgrFilter').value;
const alias=document.getElementById('aliasFilter').value;

let groupBy='team';
let groupTitle='Team';
if(alias){{groupBy='alias';groupTitle='Alias';}}
else if(mgr){{groupBy='mgr';groupTitle='Mgr';}}
else if(team){{groupBy='team';groupTitle='Team';}}

// Group data
const groupData={{}};
plans.forEach(p=>{{
const groupKey=p[groupBy]||'Unknown';
if(!groupData[groupKey]){{
groupData[groupKey]={{
sellers:0,curGMS:0,tgtGMS:0,gap:0,
sourcing:0,suppression:0,both:0,maintain:0,
noSupp:0,oos:0,vrp:0,priceError:0,others:0,
totalWeight:0
}};
}}
const d=groupData[groupKey];
d.sellers++;
d.curGMS+=p.current_gms;
d.tgtGMS+=p.target_gms;
d.gap+=p.gap;
// Calculate action focus with new logic
const c=calcProjectedOPS(p.cid,p.current_gms,p.target_gms,p.sshve1_suppression,p.sshve2_suppression);
const opsVsTarget=c.projOPS-c.targetOPS;
const gmsVsTarget=p.gap;
const noSuppDiff=p.sshve2_suppression['No suppression']-p.sshve1_suppression['No suppression'];
// Maintain: OPS vs Target >= 0 AND GMS vs Target >= 0 AND No Supp >= SSHVE1
if(opsVsTarget>=0&&gmsVsTarget>=0&&noSuppDiff>=0){{d.maintain++;}}
// Suppression: GMS vs Target >= 0 BUT No Supp < SSHVE1
else if(gmsVsTarget>=0&&noSuppDiff<0){{d.suppression++;}}
// Sourcing: GMS vs Target < 0 BUT No Supp >= SSHVE1
else if(gmsVsTarget<0&&noSuppDiff>=0){{d.sourcing++;}}
// Both: GMS vs Target < 0 AND No Supp < SSHVE1
else{{d.both++;}}
// Aggregate suppression percentages (weighted by current GMS)
if(p.current_gms>0){{
d.noSupp+=p.sshve2_suppression['No suppression']*p.current_gms;
d.oos+=p.sshve2_suppression['OOS']*p.current_gms;
d.vrp+=p.sshve2_suppression['VRP Missing']*p.current_gms;
d.priceError+=p.sshve2_suppression['Price Error']*p.current_gms;
d.others+=p.sshve2_suppression['Others']*p.current_gms;
d.totalWeight+=p.current_gms;
}}
}});

let teamHTML='<div style="background:#fff;padding:25px;border-radius:12px;box-shadow:0 4px 15px rgba(0,0,0,0.1);margin-bottom:30px">';
teamHTML+=`<h3 style="margin-bottom:20px;color:#1e3c72;text-align:center">📊 ${{groupTitle}} Summary</h3>`;
teamHTML+='<table style="width:100%;border-collapse:collapse;font-size:0.9em">';
teamHTML+='<thead style="background:#f8f9fa"><tr>';
teamHTML+=`<th style="padding:12px;text-align:left;border-bottom:2px solid #dee2e6;color:#2c3e50">${{groupTitle}}</th>`;
teamHTML+='<th style="padding:12px;text-align:right;border-bottom:2px solid #dee2e6;color:#2c3e50">Sellers</th>';
teamHTML+='<th style="padding:12px;text-align:right;border-bottom:2px solid #dee2e6;color:#2c3e50">Current GMS</th>';
teamHTML+='<th style="padding:12px;text-align:right;border-bottom:2px solid #dee2e6;color:#2c3e50">Target GMS</th>';
teamHTML+='<th style="padding:12px;text-align:right;border-bottom:2px solid #dee2e6;color:#2c3e50">Gap</th>';
teamHTML+='<th style="padding:12px;text-align:center;border-bottom:2px solid #dee2e6;color:#2c3e50">No Supp%</th>';
teamHTML+='<th style="padding:12px;text-align:center;border-bottom:2px solid #dee2e6;color:#2c3e50">OOS%</th>';
teamHTML+='<th style="padding:12px;text-align:center;border-bottom:2px solid #dee2e6;color:#2c3e50">Price Err%</th>';
teamHTML+='<th style="padding:12px;text-align:center;border-bottom:2px solid #dee2e6;color:#2c3e50">Others%</th>';
teamHTML+='<th style="padding:12px;text-align:center;border-bottom:2px solid #dee2e6;color:#2c3e50">🎯 Sourcing<br>(Sellers)</th>';
teamHTML+='<th style="padding:12px;text-align:center;border-bottom:2px solid #dee2e6;color:#2c3e50">🔧 Suppression<br>(Sellers)</th>';
teamHTML+='<th style="padding:12px;text-align:center;border-bottom:2px solid #dee2e6;color:#2c3e50">📊 Both<br>(Sellers)</th>';
teamHTML+='<th style="padding:12px;text-align:center;border-bottom:2px solid #dee2e6;color:#2c3e50">✅ Maintain<br>(Sellers)</th>';
teamHTML+='</tr></thead><tbody>';
Object.keys(groupData).sort().forEach(group=>{{
const d=groupData[group];
const avgNoSupp=d.totalWeight>0?d.noSupp/d.totalWeight:0;
const avgOOS=d.totalWeight>0?d.oos/d.totalWeight:0;
const avgPriceError=d.totalWeight>0?d.priceError/d.totalWeight:0;
const avgOthers=d.totalWeight>0?d.others/d.totalWeight:0;
teamHTML+=`<tr>`;
teamHTML+=`<td style="padding:12px;border-bottom:1px solid #dee2e6;font-weight:700;color:#2c3e50">${{group}}</td>`;
teamHTML+=`<td style="padding:12px;text-align:right;border-bottom:1px solid #dee2e6;color:#2c3e50">${{d.sellers}}</td>`;
teamHTML+=`<td style="padding:12px;text-align:right;border-bottom:1px solid #dee2e6;font-family:Consolas,monospace;color:#2c3e50">${{fmt(d.curGMS)}}</td>`;
teamHTML+=`<td style="padding:12px;text-align:right;border-bottom:1px solid #dee2e6;font-family:Consolas,monospace;color:#2c3e50">${{fmt(d.tgtGMS)}}</td>`;
teamHTML+=`<td style="padding:12px;text-align:right;border-bottom:1px solid #dee2e6;font-family:Consolas,monospace;color:${{d.gap>=0?'#28a745':'#dc3545'}}">${{fmt(d.gap)}}</td>`;
teamHTML+=`<td style="padding:12px;text-align:center;border-bottom:1px solid #dee2e6;color:#2c3e50">${{pct(avgNoSupp)}}</td>`;
teamHTML+=`<td style="padding:12px;text-align:center;border-bottom:1px solid #dee2e6;color:#2c3e50">${{pct(avgOOS)}}</td>`;
teamHTML+=`<td style="padding:12px;text-align:center;border-bottom:1px solid #dee2e6;color:#2c3e50">${{pct(avgPriceError)}}</td>`;
teamHTML+=`<td style="padding:12px;text-align:center;border-bottom:1px solid #dee2e6;color:#2c3e50">${{pct(avgOthers)}}</td>`;
teamHTML+=`<td style="padding:12px;text-align:center;border-bottom:1px solid #dee2e6;color:#2c3e50">${{d.sourcing}}</td>`;
teamHTML+=`<td style="padding:12px;text-align:center;border-bottom:1px solid #dee2e6;color:#2c3e50">${{d.suppression}}</td>`;
teamHTML+=`<td style="padding:12px;text-align:center;border-bottom:1px solid #dee2e6;color:#2c3e50">${{d.both}}</td>`;
teamHTML+=`<td style="padding:12px;text-align:center;border-bottom:1px solid #dee2e6;color:#2c3e50">${{d.maintain}}</td>`;
teamHTML+=`</tr>`;
}});
teamHTML+='</tbody></table></div>';
document.getElementById('teamSummarySection').innerHTML=teamHTML;
}}

function renderSummaryTables(forecastOPS,projectedOPS,targetOPS){{
document.getElementById('summarySection').style.display='block';

// Forecast vs Target
const forecastVsTarget=forecastOPS-targetOPS;
document.getElementById('forecastOPS').textContent=fmt(forecastOPS);
document.getElementById('targetOPS1').textContent=fmt(targetOPS);
document.getElementById('forecastVsTarget').textContent=fmt(forecastVsTarget);
document.getElementById('forecastVsTarget').style.color=forecastVsTarget>=0?'#28a745':'#dc3545';

// Projected vs Target
const projectedVsTarget=projectedOPS-targetOPS;
document.getElementById('projectedOPS').textContent=fmt(projectedOPS);
document.getElementById('targetOPS2').textContent=fmt(targetOPS);
document.getElementById('projectedVsTarget').textContent=fmt(projectedVsTarget);
document.getElementById('projectedVsTarget').style.color=projectedVsTarget>=0?'#28a745':'#dc3545';
}}

function sortTable(colIndex){{
if(!window.currentPlans||window.currentPlans.length===0)return;
if(currentSortColumn===colIndex){{
currentSortDirection=currentSortDirection==='asc'?'desc':'asc';
}}else{{
currentSortColumn=colIndex;
currentSortDirection='asc';
}}
const sorted=[...window.currentPlans];
sorted.sort((a,b)=>{{
let valA,valB;
// Map column index to data field
switch(colIndex){{
case 0:valA=a.cid;valB=b.cid;break;
case 1:valA=a.merchant_name||'';valB=b.merchant_name||'';break;
case 2:valA=a.alias||'';valB=b.alias||'';break;
case 3:valA=a.mgr||'';valB=b.mgr||'';break;
case 4:valA=a.team||'';valB=b.team||'';break;
case 5:{{
// Action Focus sorting: Maintain=0, Suppression=1, Sourcing=2, Both=3
const cA=calcProjectedOPS(a.cid,a.current_gms,a.target_gms,a.sshve1_suppression,a.sshve2_suppression);
const opsVsTargetA=cA.projOPS-cA.targetOPS;
const gmsVsTargetA=a.gap;
const noSuppDiffA=a.sshve2_suppression['No suppression']-a.sshve1_suppression['No suppression'];
if(opsVsTargetA>=0&&gmsVsTargetA>=0&&noSuppDiffA>=0){{valA=0;}} // Maintain
else if(gmsVsTargetA>=0&&noSuppDiffA<0){{valA=1;}} // Suppression
else if(gmsVsTargetA<0&&noSuppDiffA>=0){{valA=2;}} // Sourcing
else{{valA=3;}} // Both
const cB=calcProjectedOPS(b.cid,b.current_gms,b.target_gms,b.sshve1_suppression,b.sshve2_suppression);
const opsVsTargetB=cB.projOPS-cB.targetOPS;
const gmsVsTargetB=b.gap;
const noSuppDiffB=b.sshve2_suppression['No suppression']-b.sshve1_suppression['No suppression'];
if(opsVsTargetB>=0&&gmsVsTargetB>=0&&noSuppDiffB>=0){{valB=0;}} // Maintain
else if(gmsVsTargetB>=0&&noSuppDiffB<0){{valB=1;}} // Suppression
else if(gmsVsTargetB<0&&noSuppDiffB>=0){{valB=2;}} // Sourcing
else{{valB=3;}} // Both
break;
}}
case 6:valA=a.current_gms;valB=b.current_gms;break;
case 7:valA=a.gap;valB=b.gap;break;
case 8:valA=a.target_gms;valB=b.target_gms;break;
case 9:valA=a.current_gms+(a.event_participation.past_participation?.sshve1_gms||0)+(a.event_participation.past_participation?.t365_gms||0);valB=b.current_gms+(b.event_participation.past_participation?.sshve1_gms||0)+(b.event_participation.past_participation?.t365_gms||0);break;
case 10:valA=a.event_participation.past_participation?.sshve1_gms||0;valB=b.event_participation.past_participation?.sshve1_gms||0;break;
case 11:valA=a.event_participation.past_participation?.t365_gms||0;valB=b.event_participation.past_participation?.t365_gms||0;break;
case 12:valA=a.sshve1_suppression['No suppression'];valB=b.sshve1_suppression['No suppression'];break;
case 13:valA=a.sshve1_suppression['OOS'];valB=b.sshve1_suppression['OOS'];break;
case 14:valA=a.sshve1_suppression['VRP Missing'];valB=b.sshve1_suppression['VRP Missing'];break;
case 15:valA=a.sshve1_suppression['Price Error'];valB=b.sshve1_suppression['Price Error'];break;
case 16:valA=a.sshve1_suppression['Others'];valB=b.sshve1_suppression['Others'];break;
case 17:valA=a.sshve2_suppression['No suppression'];valB=b.sshve2_suppression['No suppression'];break;
case 18:valA=a.sshve2_suppression['OOS'];valB=b.sshve2_suppression['OOS'];break;
case 19:valA=a.sshve2_suppression['VRP Missing'];valB=b.sshve2_suppression['VRP Missing'];break;
case 20:valA=a.sshve2_suppression['Price Error'];valB=b.sshve2_suppression['Price Error'];break;
case 21:valA=a.sshve2_suppression['Others'];valB=b.sshve2_suppression['Others'];break;
case 22:{{const cA=calcProjectedOPS(a.cid,a.current_gms,a.target_gms,a.sshve1_suppression,a.sshve2_suppression);valA=cA.forecastOPS;const cB=calcProjectedOPS(b.cid,b.current_gms,b.target_gms,b.sshve1_suppression,b.sshve2_suppression);valB=cB.forecastOPS;break;}}
case 23:{{const cA=calcProjectedOPS(a.cid,a.current_gms,a.target_gms,a.sshve1_suppression,a.sshve2_suppression);valA=cA.forecastOPS-cA.targetOPS;const cB=calcProjectedOPS(b.cid,b.current_gms,b.target_gms,b.sshve1_suppression,b.sshve2_suppression);valB=cB.forecastOPS-cB.targetOPS;break;}}
case 24:{{const cA=calcProjectedOPS(a.cid,a.current_gms,a.target_gms,a.sshve1_suppression,a.sshve2_suppression);valA=cA.targetOPS;const cB=calcProjectedOPS(b.cid,b.current_gms,b.target_gms,b.sshve1_suppression,b.sshve2_suppression);valB=cB.targetOPS;break;}}
case 25:{{const cA=calcProjectedOPS(a.cid,a.current_gms,a.target_gms,a.sshve1_suppression,a.sshve2_suppression);valA=cA.srcImp;const cB=calcProjectedOPS(b.cid,b.current_gms,b.target_gms,b.sshve1_suppression,b.sshve2_suppression);valB=cB.srcImp;break;}}
case 26:valA=userInputs[a.cid]?.oosImprovement||0;valB=userInputs[b.cid]?.oosImprovement||0;break;
case 27:valA=userInputs[a.cid]?.priceErrorReduction||0;valB=userInputs[b.cid]?.priceErrorReduction||0;break;
case 28:valA=userInputs[a.cid]?.otherSuppReduction||0;valB=userInputs[b.cid]?.otherSuppReduction||0;break;
case 29:{{const cA=calcProjectedOPS(a.cid,a.current_gms,a.target_gms,a.sshve1_suppression,a.sshve2_suppression);valA=cA.suppImp;const cB=calcProjectedOPS(b.cid,b.current_gms,b.target_gms,b.sshve1_suppression,b.sshve2_suppression);valB=cB.suppImp;break;}}
case 30:{{const cA=calcProjectedOPS(a.cid,a.current_gms,a.target_gms,a.sshve1_suppression,a.sshve2_suppression);valA=cA.projOPS;const cB=calcProjectedOPS(b.cid,b.current_gms,b.target_gms,b.sshve1_suppression,b.sshve2_suppression);valB=cB.projOPS;break;}}
case 31:{{const cA=calcProjectedOPS(a.cid,a.current_gms,a.target_gms,a.sshve1_suppression,a.sshve2_suppression);valA=cA.incOPS;const cB=calcProjectedOPS(b.cid,b.current_gms,b.target_gms,b.sshve1_suppression,b.sshve2_suppression);valB=cB.incOPS;break;}}
case 32:{{const cA=calcProjectedOPS(a.cid,a.current_gms,a.target_gms,a.sshve1_suppression,a.sshve2_suppression);valA=cA.vsTarget;const cB=calcProjectedOPS(b.cid,b.current_gms,b.target_gms,b.sshve1_suppression,b.sshve2_suppression);valB=cB.vsTarget;break;}}
default:return 0;
}}
if(typeof valA==='string'){{
return currentSortDirection==='asc'?valA.localeCompare(valB):valB.localeCompare(valA);
}}
return currentSortDirection==='asc'?(valA-valB):(valB-valA);
}});
window.currentPlans=sorted;
renderTableContent(sorted);
}}

function renderTable(plans){{
const cont=document.getElementById('resultsSection');
const bulk=document.getElementById('bulkSection');
if(plans.length===0){{
cont.innerHTML='<div class="empty"><h3>❌ データなし</h3></div>';
document.getElementById('statsSection').innerHTML='';
document.getElementById('teamSummarySection').innerHTML='';
document.getElementById('summarySection').style.display='none';
bulk.style.display='none';
return;
}}
window.currentPlans=plans;
currentSortColumn=null;
currentSortDirection='asc';
renderStats(plans);
bulk.style.display='block';
renderTableContent(plans);
}}

function getSortIndicator(colIndex){{
if(currentSortColumn!==colIndex)return'';
return currentSortDirection==='asc'?'<span class="sort-indicator">▲</span>':'<span class="sort-indicator">▼</span>';
}}

function renderTableContent(plans){{
const cont=document.getElementById('resultsSection');
let h='<div class="table-container"><table><thead><tr>';
h+='<th rowspan="2" onclick="sortTable(0)">CID'+getSortIndicator(0)+'</th>';
h+='<th rowspan="2" onclick="sortTable(1)">Merchant<br>Name'+getSortIndicator(1)+'</th>';
h+='<th rowspan="2" onclick="sortTable(2)">Alias'+getSortIndicator(2)+'</th>';
h+='<th rowspan="2" onclick="sortTable(3)">Mgr'+getSortIndicator(3)+'</th>';
h+='<th rowspan="2" onclick="sortTable(4)">Team'+getSortIndicator(4)+'</th>';
h+='<th rowspan="2" onclick="sortTable(5)">Action<br>Focus'+getSortIndicator(5)+'</th>';
h+='<th colspan="4">Sourced GMS</th><th colspan="2">今回不参加だが<br>過去参加ASINの<br>T30 GMS</th>';
h+='<th colspan="5">SSHVE1 Suppression<br><span style="font-size:0.65em;font-weight:400;opacity:0.9">※SS HVE1 SuppressionデータがないセラーはPF平均の数字を使用</span></th><th colspan="5">SSHVE2 Suppression</th>';
h+='<th colspan="3">Promotion OPS</th>';
h+='<th rowspan="2" onclick="sortTable(25)">Sourcing<br>改善幅<br>(金額)'+getSortIndicator(25)+'</th>';
h+='<th rowspan="2" onclick="sortTable(26)">OOS<br>改善率<br>(%)'+getSortIndicator(26)+'</th>';
h+='<th rowspan="2" onclick="sortTable(27)">Price Error<br>削減率<br>(%)'+getSortIndicator(27)+'</th>';
h+='<th rowspan="2" onclick="sortTable(28)">その他Supp<br>削減率<br>(%)'+getSortIndicator(28)+'</th>';
h+='<th rowspan="2" onclick="sortTable(29)">Suppression<br>改善幅<br>(金額)'+getSortIndicator(29)+'</th>';
h+='<th rowspan="2" onclick="sortTable(30)">Projected<br>OPS'+getSortIndicator(30)+'</th>';
h+='<th rowspan="2" onclick="sortTable(31)">Incremental<br>OPS'+getSortIndicator(31)+'</th>';
h+='<th rowspan="2" onclick="sortTable(32)">vs Target<br>(Projected OPS-Target OPS)'+getSortIndicator(32)+'</th></tr>';
h+='<tr>';
h+='<th onclick="sortTable(6)">Act'+getSortIndicator(6)+'</th>';
h+='<th onclick="sortTable(7)">vs Target'+getSortIndicator(7)+'</th>';
h+='<th onclick="sortTable(8)">Target'+getSortIndicator(8)+'</th>';
h+='<th onclick="sortTable(9)">Total GMS'+getSortIndicator(9)+'</th>';
h+='<th onclick="sortTable(10)">SSHVE1'+getSortIndicator(10)+'</th>';
h+='<th onclick="sortTable(11)">T365'+getSortIndicator(11)+'</th>';
h+='<th onclick="sortTable(12)">No Supp'+getSortIndicator(12)+'</th>';
h+='<th onclick="sortTable(13)">OOS'+getSortIndicator(13)+'</th>';
h+='<th onclick="sortTable(14)">VRP'+getSortIndicator(14)+'</th>';
h+='<th onclick="sortTable(15)">Price'+getSortIndicator(15)+'</th>';
h+='<th onclick="sortTable(16)">Others'+getSortIndicator(16)+'</th>';
h+='<th onclick="sortTable(17)">No Supp'+getSortIndicator(17)+'</th>';
h+='<th onclick="sortTable(18)">OOS'+getSortIndicator(18)+'</th>';
h+='<th onclick="sortTable(19)">VRP'+getSortIndicator(19)+'</th>';
h+='<th onclick="sortTable(20)">Price'+getSortIndicator(20)+'</th>';
h+='<th onclick="sortTable(21)">Others'+getSortIndicator(21)+'</th>';
h+='<th onclick="sortTable(22)">Forecast'+getSortIndicator(22)+'</th>';
h+='<th onclick="sortTable(23)">vs Target'+getSortIndicator(23)+'</th>';
h+='<th onclick="sortTable(24)">Target'+getSortIndicator(24)+'</th>';
h+='</tr></thead><tbody>';
plans.forEach(p=>{{
const c=calcProjectedOPS(p.cid,p.current_gms,p.target_gms,p.sshve1_suppression,p.sshve2_suppression);
// New Action Focus logic based on Promotion OPS vs Target, Sourced GMS vs Target, and No Suppression comparison
const opsVsTarget=c.projOPS-c.targetOPS;
const gmsVsTarget=p.gap; // gap = current_gms - target_gms
const noSuppDiff=p.sshve2_suppression['No suppression']-p.sshve1_suppression['No suppression'];
let actionRec='';
// Maintain: OPS vs Target > 0 AND GMS vs Target > 0 AND No Supp >= SSHVE1
if(opsVsTarget>=0&&gmsVsTarget>=0&&noSuppDiff>=0){{
actionRec='✅ Maintain';
}}
// Suppression: GMS vs Target > 0 BUT No Supp < SSHVE1
else if(gmsVsTarget>=0&&noSuppDiff<0){{
actionRec='🔧 Suppression';
}}
// Sourcing: GMS vs Target < 0 BUT No Supp >= SSHVE1
else if(gmsVsTarget<0&&noSuppDiff>=0){{
actionRec='🎯 Sourcing';
}}
// Both: GMS vs Target < 0 AND No Supp < SSHVE1
else{{
actionRec='📊 Both';
}}
h+='<tr>';
h+=`<td><a href="https://us-east-1.quicksight.aws.amazon.com/sn/account/amazonbi/dashboards/863e3abc-b6f2-421d-9b11-dee511261bad/sheets/863e3abc-b6f2-421d-9b11-dee511261bad_d274b393-3f0a-4573-bab8-a67d87d50ec9" target="_blank" style="color:#1e3c72;text-decoration:none" title="View in QuickSight">${{p.cid}}</a></td>`;
h+=`<td>${{p.merchant_name||'-'}}</td>`;
h+=`<td>${{p.alias||'-'}}</td>`;
h+=`<td>${{p.mgr||'-'}}</td>`;
h+=`<td>${{p.team||'-'}}</td>`;
h+=`<td style="text-align:center;font-weight:700">${{actionRec}}</td>`;
h+=`<td class="number">${{fmt(p.current_gms)}}</td>`;
h+=`<td class="number ${{p.gap>=0?'positive':'negative'}}">${{fmt(p.gap)}}</td>`;
h+=`<td class="number">${{fmt(p.target_gms)}}</td>`;
h+=`<td class="number">${{fmt(p.current_gms+(p.event_participation.past_participation?.sshve1_gms||0)+(p.event_participation.past_participation?.t365_gms||0))}}</td>`;
h+=`<td class="number">${{fmt(p.event_participation.past_participation?.sshve1_gms||0)}}</td>`;
h+=`<td class="number">${{fmt(p.event_participation.past_participation?.t365_gms||0)}}</td>`;
['No suppression','OOS','VRP Missing','Price Error','Others'].forEach(cat=>{{
const isFallback=p.sshve1_suppression_fallback||false;
const style=isFallback?'background:#e0e0e0;font-style:italic':'';
const title=isFallback?'PF平均値を使用':'';
h+=`<td class="number" style="${{style}}" title="${{title}}">${{pct(p.sshve1_suppression[cat])}}</td>`;
}});
['No suppression','OOS','VRP Missing','Price Error','Others'].forEach(cat=>{{
h+=`<td class="number">${{pct(p.sshve2_suppression[cat])}}</td>`;
}});
h+=`<td class="number">${{fmt(c.forecastOPS)}}</td>`;
h+=`<td class="number ${{(c.forecastOPS-c.targetOPS)>=0?'positive':'negative'}}">${{fmt(c.forecastOPS-c.targetOPS)}}</td>`;
h+=`<td class="number">${{fmt(c.targetOPS)}}</td>`;
h+=`<td class="number editable" onclick="edit(this,'${{p.cid}}','sourcing')">${{fmt(c.srcImp)}}</td>`;
h+=`<td class="number editable" onclick="edit(this,'${{p.cid}}','oosImprovement')">${{pct(userInputs[p.cid]?.oosImprovement||0)}}</td>`;
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

function updateCascadingFilters(){{
const team=document.getElementById('teamFilter').value;
const mgr=document.getElementById('mgrFilter').value;
const alias=document.getElementById('aliasFilter').value;

// Filter data based on current selections
let filtered=ALL_DATA;
if(team)filtered=filtered.filter(c=>c.team===team);
if(mgr)filtered=filtered.filter(c=>c.mgr===mgr);
if(alias)filtered=filtered.filter(c=>c.alias===alias);

// Update Mgr options based on Team
const mgrSelect=document.getElementById('mgrFilter');
const currentMgr=mgrSelect.value;
const mgrs=team?[...new Set(ALL_DATA.filter(c=>c.team===team).map(c=>c.mgr).filter(m=>m))].sort():[...new Set(ALL_DATA.map(c=>c.mgr).filter(m=>m))].sort();
mgrSelect.innerHTML='<option value="">-- Select --</option>'+mgrs.map(m=>`<option value="${{m}}" ${{m===currentMgr?'selected':''}}>${{m}}</option>`).join('');

// Update Alias options based on Team and Mgr
const aliasSelect=document.getElementById('aliasFilter');
const currentAlias=aliasSelect.value;
let aliasFiltered=ALL_DATA;
if(team)aliasFiltered=aliasFiltered.filter(c=>c.team===team);
if(mgr)aliasFiltered=aliasFiltered.filter(c=>c.mgr===mgr);
const aliases=[...new Set(aliasFiltered.map(c=>c.alias).filter(a=>a))].sort();
aliasSelect.innerHTML='<option value="">-- Select --</option>'+aliases.map(a=>`<option value="${{a}}" ${{a===currentAlias?'selected':''}}>${{a}}</option>`).join('');

// Update Merchant options based on all previous filters
const merchantSelect=document.getElementById('merchantFilter');
const merchants=[...new Set(filtered.map(c=>c.merchant_name).filter(m=>m))].sort();
merchantSelect.innerHTML='<option value="">-- Select --</option>'+merchants.map(m=>`<option value="${{m}}">${{m}}</option>`).join('');
}}

function filterData(){{
const team=document.getElementById('teamFilter').value;
const mgr=document.getElementById('mgrFilter').value;
const alias=document.getElementById('aliasFilter').value;
const mcid=document.getElementById('mcidFilter').value.trim();
const merchant=document.getElementById('merchantFilter').value;
console.log('Filter values:',{{team,mgr,alias,mcid,merchant}});
if(!team&&!mgr&&!alias&&!mcid&&!merchant){{alert('⚠️ フィルター選択');return}}
const filtered=ALL_DATA.filter(c=>{{
if(team&&c.team!==team)return false;
if(mgr&&c.mgr!==mgr)return false;
if(alias&&c.alias!==alias)return false;
if(mcid&&!c.cid.includes(mcid))return false;
if(merchant&&c.merchant_name!==merchant)return false;
return true;
}});
console.log('Filtered results:',filtered.length);
renderTable(filtered);
}}

function resetFilter(){{
document.getElementById('teamFilter').value='';
document.getElementById('mgrFilter').value='';
document.getElementById('aliasFilter').value='';
document.getElementById('mcidFilter').value='';
document.getElementById('merchantFilter').value='';
updateCascadingFilters();
document.getElementById('headerInfo').innerHTML=`📊 {len(data['cids'])} MCIDs (Total) | 🔄 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}`;
document.getElementById('resultsSection').innerHTML='<div class="empty"><h3>📋 フィルターを選択してください</h3></div>';
document.getElementById('statsSection').innerHTML='';
document.getElementById('teamSummarySection').innerHTML='';
document.getElementById('summarySection').style.display='none';
document.getElementById('bulkSection').style.display='none';
}}

function exportCSV(){{
if(!window.currentPlans||window.currentPlans.length===0){{alert('⚠️ データなし');return}}
const headers=['CID','Merchant Name','Alias','Mgr','Team','Current GMS','vs Target','Target GMS','Total GMS',
'Past SSHVE1 GMS','Past T365 GMS','SS1 No Supp%','SS1 OOS%','SS1 VRP%','SS1 Price%','SS1 Others%',
'SS2 No Supp%','SS2 OOS%','SS2 VRP%','SS2 Price%','SS2 Others%',
'Forecast OPS','vs Target OPS','Target OPS','Sourcing Imp','OOS Imp%','Price Error Red%','Other Supp Red%',
'Suppression Imp','Projected OPS','Incremental OPS','vs Target'];
let csv=headers.join(',')+`\\n`;
window.currentPlans.forEach(p=>{{
const c=calcProjectedOPS(p.cid,p.current_gms,p.target_gms,p.sshve1_suppression,p.sshve2_suppression);
const totalGMS=p.current_gms+(p.event_participation.past_participation?.sshve1_gms||0)+(p.event_participation.past_participation?.t365_gms||0);
const row=[p.cid,p.merchant_name||'-',p.alias||'-',p.mgr||'-',p.team||'-',p.current_gms,p.gap,p.target_gms,totalGMS,
p.event_participation.past_participation?.sshve1_gms||0,p.event_participation.past_participation?.t365_gms||0,
p.sshve1_suppression['No suppression'],p.sshve1_suppression['OOS'],p.sshve1_suppression['VRP Missing'],
p.sshve1_suppression['Price Error'],p.sshve1_suppression['Others'],
p.sshve2_suppression['No suppression'],p.sshve2_suppression['OOS'],p.sshve2_suppression['VRP Missing'],
p.sshve2_suppression['Price Error'],p.sshve2_suppression['Others'],
c.forecastOPS,c.forecastOPS-c.targetOPS,c.targetOPS,c.srcImp,
userInputs[p.cid]?.oosImprovement||0,userInputs[p.cid]?.priceErrorReduction||0,userInputs[p.cid]?.otherSuppReduction||0,
c.suppImp,c.projOPS,c.incOPS,c.vsTarget];
csv+=row.join(',')+`\\n`;
}});
// Add UTF-8 BOM to fix character encoding issues in Excel
const BOM='\\uFEFF';
const blob=new Blob([BOM+csv],{{type:'text/csv;charset=utf-8;'}});
const link=document.createElement('a');
link.href=URL.createObjectURL(blob);
link.download=`sshve2_final_${{new Date().toISOString().slice(0,10)}}.csv`;
link.click();
}}
</script>
</body>
</html>'''

with open(output, 'w', encoding='utf-8') as f:
    f.write(html)

print(f"\n✅ Created: {output}")
print(f"📊 Size: {len(html)/1024:.2f} KB")
print(f"📊 Suppression data size: {len(suppression_data_js)/1024:.2f} KB")
print("\n" + "=" * 80)
print("✨ 完成! SSHVE2 Opportunity Dashboard:")
print("  ✅ Sourced GMS: SSHVE2_SourcedFlag=Yのみ")
print("  ✅ 今回不参加だが過去参加ASIN: GMS表示")
print("  ✅ No Suppression Rate: GMS加重平均")
print("  ✅ Forecast/Projected vs Target: 数値表で表示")
print("=" * 80)
