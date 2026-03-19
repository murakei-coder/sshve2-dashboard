"""スタンドアロンHTMLダッシュボードを生成"""

import pandas as pd
import json
import sys
from datetime import datetime
from pathlib import Path


def generate_standalone_dashboard(data_file, seller_file, top40k_file, output_file='standalone_dashboard.html'):
    """
    データを埋め込んだスタンドアロンHTMLダッシュボードを生成
    
    Parameters:
        data_file: データファイルパス
        seller_file: セラーリストファイルパス
        top40k_file: Top40Kトラッキングファイルパス
        output_file: 出力HTMLファイルパス
    """
    print("=" * 80)
    print("スタンドアロンダッシュボード生成中...")
    print("=" * 80)
    
    # データを読み込み
    print(f"データファイルを読み込み中: {data_file}")
    df = pd.read_csv(data_file, sep='\t', encoding='utf-8')
    print(f"  ✓ {len(df)}行を読み込みました")
    
    # セラーリストを読み込み
    print(f"セラーリストを読み込み中: {seller_file}")
    seller_df = pd.read_excel(seller_file)
    print(f"  ✓ {len(seller_df)}件のセラー情報を読み込みました")
    
    # Top40Kリストを読み込み
    print(f"Top40Kリストを読み込み中: {top40k_file}")
    top40k_df = pd.read_excel(top40k_file, sheet_name='Top40K List')
    print(f"  ✓ {len(top40k_df)}件のTop40K情報を読み込みました")
    
    # Top40KデータとSellerデータを結合してTeam/Aliasを追加
    if 'CID' in top40k_df.columns and 'merchant_customer_id' in seller_df.columns:
        top40k_df = top40k_df.merge(
            seller_df[['merchant_customer_id', 'team', 'alias']], 
            left_on='CID', 
            right_on='merchant_customer_id', 
            how='left'
        )
        top40k_df['team'] = top40k_df['team'].fillna('Unknown')
        top40k_df['alias'] = top40k_df['alias'].fillna('Unknown')
        print(f"  ✓ Top40KデータにTeam/Alias情報を追加しました")
    
    # データを結合
    print("データを結合中...")
    if 'merchant_customer_id' in df.columns and 'merchant_customer_id' in seller_df.columns:
        df = df.merge(seller_df[['merchant_customer_id', 'team', 'alias']], 
                     on='merchant_customer_id', 
                     how='left')
        df['team'] = df['team'].fillna('Unknown')
        df['alias'] = df['alias'].fillna('Unknown')
    print(f"  ✓ データを結合しました")
    
    # JSONに変換
    print("データをJSON形式に変換中...")
    
    # データ分析用：集計済みデータのみを作成（生データは埋め込まない）
    print("集計データを作成中...")
    
    # PF/GL集計
    pf_gl_agg = df.groupby(['pf', 'gl']).agg({
        'total_t30d_gms': 'sum',
        'total_promotion_ops': 'sum'
    }).reset_index().to_dict('records')
    
    # Top20K/40K集計（PF別）
    def categorize_top(row):
        if row['is_top_20k'] == 'Y':
            return 'Top 20K'
        elif row['is_top_40k'] == 'Y':
            return 'Top 40K'
        else:
            return 'Others'
    
    df['category'] = df.apply(categorize_top, axis=1)
    topk_agg = df.groupby(['pf', 'category']).agg({
        'total_promotion_ops': 'sum'
    }).reset_index().to_dict('records')
    
    # Suppression Status集計
    suppression_agg = df.groupby('suppression_status').agg({
        'total_t30d_gms': 'sum',
        'total_promotion_ops': 'sum'
    }).reset_index().to_dict('records')
    
    # Top40Kデータ（Sourcing Rate用）
    top40k_json = top40k_df.to_dict('records')
    
    # フィルター用のユニーク値を取得
    pf_values = sorted(df['pf'].unique().tolist())
    gl_values = sorted(df['gl'].unique().tolist())
    team_values = sorted(top40k_df['team'].unique().tolist())
    alias_values = sorted(top40k_df['alias'].unique().tolist())
    
    aggregated_data = {
        'pf_gl': pf_gl_agg,
        'topk': topk_agg,
        'suppression': suppression_agg,
        'pf_values': pf_values,
        'gl_values': gl_values,
        'team_values': team_values,
        'alias_values': alias_values
    }
    
    columns = df.columns.tolist()
    
    # メタデータ
    metadata = {
        'generated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'total_rows': len(df),
        'total_columns': len(df.columns),
        'data_file': data_file,
        'seller_file': seller_file,
        'top40k_file': top40k_file
    }
    
    # HTMLを生成
    print("HTMLファイルを生成中...")
    html_content = generate_html(aggregated_data, top40k_json, columns, metadata)
    
    # ファイルに保存
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    abs_path = Path(output_file).resolve()
    print(f"\n{'='*80}")
    print(f"✓ スタンドアロンダッシュボードを生成しました")
    print(f"{'='*80}")
    print(f"ファイル: {abs_path}")
    print(f"行数: {len(df):,}")
    print(f"列数: {len(df.columns)}")
    print(f"\nこのHTMLファイルを他の人に共有してください。")
    print(f"受け取った人はダブルクリックするだけで使えます（Pythonなしで動作）。")
    
    return str(abs_path)


def generate_html(aggregated_data, top40k_data, columns, metadata):
    """HTMLコンテンツを生成"""
    
    # データをJavaScript変数として埋め込み
    aggregated_js = json.dumps(aggregated_data, ensure_ascii=False)
    top40k_js = json.dumps(top40k_data, ensure_ascii=False)
    metadata_js = json.dumps(metadata, ensure_ascii=False)
    
    html = f'''<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Data Analysis Dashboard</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ 
            font-family: 'Segoe UI', 'Meiryo', sans-serif; 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}
        .container {{ 
            max-width: 1800px; 
            margin: 0 auto; 
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
        }}
        .header {{
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            color: white;
            padding: 40px;
        }}
        .header h1 {{ font-size: 2.5em; margin-bottom: 10px; }}
        .header p {{ opacity: 0.8; font-size: 1.1em; }}
        .metadata {{
            background: rgba(255,255,255,0.1);
            border-radius: 10px;
            padding: 20px;
            margin-top: 20px;
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
        }}
        .metadata-item {{
            display: flex;
            flex-direction: column;
        }}
        .metadata-label {{
            font-size: 0.9em;
            opacity: 0.7;
            margin-bottom: 5px;
        }}
        .metadata-value {{
            font-size: 1.1em;
            font-weight: bold;
        }}
        .content {{ padding: 40px; }}
        .filter-section {{
            background: #f8f9fa;
            border-radius: 15px;
            padding: 30px;
            margin-bottom: 30px;
        }}
        .filter-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }}
        .filter-group {{
            display: flex;
            flex-direction: column;
        }}
        .filter-group label {{
            font-weight: 600;
            margin-bottom: 8px;
            color: #333;
        }}
        .filter-group select {{
            padding: 10px;
            border: 2px solid #e0e0e0;
            border-radius: 8px;
            font-size: 1em;
        }}
        .btn {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 12px 30px;
            border-radius: 10px;
            font-size: 1em;
            font-weight: 600;
            cursor: pointer;
            transition: transform 0.2s;
            margin-right: 10px;
        }}
        .btn:hover {{
            transform: translateY(-2px);
        }}
        .btn-secondary {{
            background: linear-gradient(135deg, #6c757d 0%, #495057 100%);
        }}
        .dashboard-section {{
            background: white;
            border-radius: 15px;
            padding: 30px;
            margin-bottom: 30px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        .table-container {{
            background: white;
            border-radius: 10px;
            overflow: hidden;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            max-height: 500px;
            overflow-y: auto;
        }}
        .data-table {{
            width: 100%;
            border-collapse: collapse;
        }}
        .data-table thead {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            position: sticky;
            top: 0;
            z-index: 10;
        }}
        .data-table th {{
            padding: 15px;
            text-align: left;
            font-weight: 600;
        }}
        .data-table td {{
            padding: 12px 15px;
            border-bottom: 1px solid #eee;
            text-align: left;
        }}
        .data-table tbody tr:hover {{
            background: #f8f9fa;
        }}
        .data-table tbody tr:nth-child(even) {{
            background: #fafafa;
        }}
        .data-table td.number {{
            text-align: right;
        }}
        .section-title {{
            font-size: 1.5em;
            color: #1a1a2e;
            border-left: 5px solid #667eea;
            padding-left: 15px;
            margin-bottom: 20px;
        }}
        .tabs {{
            display: flex;
            gap: 10px;
            margin-bottom: 30px;
            border-bottom: 2px solid #e0e0e0;
        }}
        .tab {{
            padding: 15px 30px;
            background: transparent;
            border: none;
            font-size: 1.1em;
            font-weight: 600;
            cursor: pointer;
            color: #666;
            border-bottom: 3px solid transparent;
            transition: all 0.3s;
        }}
        .tab:hover {{
            color: #667eea;
        }}
        .tab.active {{
            color: #667eea;
            border-bottom-color: #667eea;
        }}
        .tab-content {{
            display: none;
        }}
        .tab-content.active {{
            display: block;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 Data Analysis Dashboard</h1>
            <p>インタラクティブデータ分析ダッシュボード</p>
            
            <div class="metadata">
                <div class="metadata-item">
                    <div class="metadata-label">生成日時</div>
                    <div class="metadata-value" id="generated_at"></div>
                </div>
                <div class="metadata-item">
                    <div class="metadata-label">総行数</div>
                    <div class="metadata-value" id="total_rows"></div>
                </div>
                <div class="metadata-item">
                    <div class="metadata-label">列数</div>
                    <div class="metadata-value" id="total_columns"></div>
                </div>
            </div>
        </div>
        
        <div class="content">
            <h2 class="section-title">� データ分析セクション</h2>
            
            <h3 class="section-title">�🔍 フィルター (PF/GL分析用)</h3>
            <div class="filter-section">
                <div class="filter-grid">
                    <div class="filter-group">
                        <label for="filter_pf">PF</label>
                        <select id="filter_pf" multiple size="5"></select>
                    </div>
                    <div class="filter-group">
                        <label for="filter_gl">GL</label>
                        <select id="filter_gl" multiple size="5"></select>
                    </div>
                </div>
                <button class="btn" onclick="applyDataFilters()">適用</button>
                <button class="btn btn-secondary" onclick="resetDataFilters()">リセット</button>
            </div>
            
            <div class="tabs">
                <button class="tab active" onclick="switchTab('tab1')">PF/GL分析</button>
                <button class="tab" onclick="switchTab('tab2')">Top20K/40K分析</button>
                <button class="tab" onclick="switchTab('tab3')">Suppression Status分析</button>
            </div>
            
            <div id="tab1" class="tab-content active">
                <div class="dashboard-section">
                    <h2 class="section-title">📊 PF/GLごとの分析</h2>
                    <div class="table-container">
                        <table class="data-table" id="pfGlTable">
                            <thead>
                                <tr>
                                    <th>PF</th>
                                    <th>GL</th>
                                    <th>T30d GMS</th>
                                    <th>Promotion OPS</th>
                                    <th>OPS/T30d GMS</th>
                                </tr>
                            </thead>
                            <tbody id="pfGlTableBody"></tbody>
                        </table>
                    </div>
                </div>
            </div>
            
            <div id="tab2" class="tab-content">
                <div class="dashboard-section">
                    <h2 class="section-title">📊 Top20K/40K分析 (By PF)</h2>
                    <div class="table-container">
                        <table class="data-table" id="topKTable">
                            <thead>
                                <tr>
                                    <th>PF</th>
                                    <th>Category</th>
                                    <th>Promotion OPS</th>
                                    <th>Mix (%)</th>
                                </tr>
                            </thead>
                            <tbody id="topKTableBody"></tbody>
                        </table>
                    </div>
                </div>
            </div>
            
            <div id="tab3" class="tab-content">
                <div class="dashboard-section">
                    <h2 class="section-title">📊 Suppression Statusごとの分析</h2>
                    <div class="table-container">
                        <table class="data-table" id="suppressionTable">
                            <thead>
                                <tr>
                                    <th>Suppression Status</th>
                                    <th>T30d GMS</th>
                                    <th>Promotion OPS</th>
                                    <th>OPS/T30d GMS</th>
                                </tr>
                            </thead>
                            <tbody id="suppressionTableBody"></tbody>
                        </table>
                    </div>
                </div>
            </div>
            
            <hr style="margin: 50px 0; border: none; border-top: 3px solid #667eea;">
            
            <h2 class="section-title">📊 Sourcing Rate分析セクション</h2>
            
            <h3 class="section-title">🔍 フィルター (Sourcing Rate分析用)</h3>
            <div class="filter-section">
                <div class="filter-grid">
                    <div class="filter-group">
                        <label for="filter_team">Team</label>
                        <select id="filter_team" multiple size="5"></select>
                    </div>
                    <div class="filter-group">
                        <label for="filter_alias">Alias</label>
                        <select id="filter_alias" multiple size="5"></select>
                    </div>
                </div>
                <button class="btn" onclick="applySourcingFilters()">適用</button>
                <button class="btn btn-secondary" onclick="resetSourcingFilters()">リセット</button>
            </div>
            
            <div class="dashboard-section">
                <h2 class="section-title">📊 Sourcing Rate分析 (CID別)</h2>
                <div class="table-container">
                    <table class="data-table" id="sourcingTable">
                        <thead>
                            <tr>
                                <th>CID (Seller)</th>
                                <th>Team</th>
                                <th>Alias</th>
                                <th>Sourced T30d GMS</th>
                                <th>Non-Sourced T30d GMS</th>
                                <th>Total T30d GMS</th>
                                <th>Sourced GMS %</th>
                            </tr>
                        </thead>
                        <tbody id="sourcingTableBody"></tbody>
                    </table>
                </div>
            </div>
            
        </div>
    </div>
    
    <script>
        // 集計済みデータを埋め込み
        const aggregatedData = {aggregated_js};
        const top40kData = {top40k_js};
        const metadata = {metadata_js};
        
        // 初期化
        document.getElementById('generated_at').textContent = metadata.generated_at;
        document.getElementById('total_rows').textContent = metadata.total_rows.toLocaleString();
        document.getElementById('total_columns').textContent = metadata.total_columns;
        
        // PF/GLフィルターのオプションを生成
        const pfSelect = document.getElementById('filter_pf');
        const glSelect = document.getElementById('filter_gl');
        
        aggregatedData.pf_values.forEach(v => {{
            const option = document.createElement('option');
            option.value = v;
            option.textContent = v;
            pfSelect.appendChild(option);
        }});
        
        aggregatedData.gl_values.forEach(v => {{
            const option = document.createElement('option');
            option.value = v;
            option.textContent = v;
            glSelect.appendChild(option);
        }});
        
        // Team/Aliasフィルターのオプションを生成
        const teamSelect = document.getElementById('filter_team');
        const aliasSelect = document.getElementById('filter_alias');
        
        aggregatedData.team_values.forEach(v => {{
            const option = document.createElement('option');
            option.value = v;
            option.textContent = v;
            teamSelect.appendChild(option);
        }});
        
        aggregatedData.alias_values.forEach(v => {{
            const option = document.createElement('option');
            option.value = v;
            option.textContent = v;
            aliasSelect.appendChild(option);
        }});
        
        // 初期表示
        updateDataDashboards();
        updateSourcingDashboard();
        
        function switchTab(tabId) {{
            // タブの切り替え
            document.querySelectorAll('.tab').forEach(tab => tab.classList.remove('active'));
            document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));
            
            event.target.classList.add('active');
            document.getElementById(tabId).classList.add('active');
        }}
        
        function applyDataFilters() {{
            updateDataDashboards();
        }}
        
        function resetDataFilters() {{
            pfSelect.selectedIndex = -1;
            glSelect.selectedIndex = -1;
            updateDataDashboards();
        }}
        
        function applySourcingFilters() {{
            updateSourcingDashboard();
        }}
        
        function resetSourcingFilters() {{
            teamSelect.selectedIndex = -1;
            aliasSelect.selectedIndex = -1;
            updateSourcingDashboard();
        }}
        
        function updateDataDashboards() {{
            updatePfGlDashboard();
            updateTopKDashboard();
            updateSuppressionDashboard();
        }}
        
        function updatePfGlDashboard() {{
            const selectedPf = Array.from(pfSelect.selectedOptions).map(opt => opt.value);
            const selectedGl = Array.from(glSelect.selectedOptions).map(opt => opt.value);
            
            let data = aggregatedData.pf_gl;
            
            // フィルタリング
            if (selectedPf.length > 0) {{
                data = data.filter(row => selectedPf.includes(row.pf));
            }}
            
            if (selectedGl.length > 0) {{
                data = data.filter(row => selectedGl.includes(row.gl));
            }}
            
            const tbody = document.getElementById('pfGlTableBody');
            tbody.innerHTML = '';
            
            data.forEach(item => {{
                const ratio = item.total_t30d_gms !== 0 ? (item.total_promotion_ops / item.total_t30d_gms) : 0;
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td>${{item.pf}}</td>
                    <td>${{item.gl}}</td>
                    <td class="number">${{item.total_t30d_gms.toLocaleString('en-US', {{minimumFractionDigits: 2, maximumFractionDigits: 2}})}}</td>
                    <td class="number">${{item.total_promotion_ops.toLocaleString('en-US', {{minimumFractionDigits: 2, maximumFractionDigits: 2}})}}</td>
                    <td class="number">${{ratio.toFixed(4)}}</td>
                `;
                tbody.appendChild(row);
            }});
        }}
        
        function updateTopKDashboard() {{
            const selectedPf = Array.from(pfSelect.selectedOptions).map(opt => opt.value);
            
            let data = aggregatedData.topk;
            
            // フィルタリング
            if (selectedPf.length > 0) {{
                data = data.filter(row => selectedPf.includes(row.pf));
            }}
            
            // PFごとの合計を計算
            const pfTotals = {{}};
            data.forEach(row => {{
                if (!pfTotals[row.pf]) {{
                    pfTotals[row.pf] = 0;
                }}
                pfTotals[row.pf] += row.total_promotion_ops;
            }});
            
            const tbody = document.getElementById('topKTableBody');
            tbody.innerHTML = '';
            
            data.forEach(item => {{
                const total = pfTotals[item.pf];
                const mix = total !== 0 ? (item.total_promotion_ops / total * 100) : 0;
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td>${{item.pf}}</td>
                    <td>${{item.category}}</td>
                    <td class="number">${{item.total_promotion_ops.toLocaleString('en-US', {{minimumFractionDigits: 2, maximumFractionDigits: 2}})}}</td>
                    <td class="number">${{mix.toFixed(2)}}%</td>
                `;
                tbody.appendChild(row);
            }});
        }}
        
        function updateSuppressionDashboard() {{
            const data = aggregatedData.suppression;
            
            const tbody = document.getElementById('suppressionTableBody');
            tbody.innerHTML = '';
            
            data.forEach(item => {{
                const ratio = item.total_t30d_gms !== 0 ? (item.total_promotion_ops / item.total_t30d_gms) : 0;
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td>${{item.suppression_status}}</td>
                    <td class="number">${{item.total_t30d_gms.toLocaleString('en-US', {{minimumFractionDigits: 2, maximumFractionDigits: 2}})}}</td>
                    <td class="number">${{item.total_promotion_ops.toLocaleString('en-US', {{minimumFractionDigits: 2, maximumFractionDigits: 2}})}}</td>
                    <td class="number">${{ratio.toFixed(4)}}</td>
                `;
                tbody.appendChild(row);
            }});
        }}
        
        function updateSourcingDashboard() {{
            const grouped = {{}};
            
            // Team/Aliasフィルターを取得
            const selectedTeam = Array.from(teamSelect.selectedOptions).map(opt => opt.value);
            const selectedAlias = Array.from(aliasSelect.selectedOptions).map(opt => opt.value);
            
            // Top40Kデータをフィルタリング
            let filteredTop40k = [...top40kData];
            
            if (selectedTeam.length > 0) {{
                filteredTop40k = filteredTop40k.filter(row => selectedTeam.includes(row['team']));
            }}
            
            if (selectedAlias.length > 0) {{
                filteredTop40k = filteredTop40k.filter(row => selectedAlias.includes(row['alias']));
            }}
            
            // CIDごとにグループ化
            filteredTop40k.forEach(row => {{
                const cid = row['CID'] || 'Unknown';
                const team = row['team'] || 'Unknown';
                const alias = row['alias'] || 'Unknown';
                const sourced = row['SSHVE1_DOTDorBD_Sourced_Final'];
                const t30gms = parseFloat(row['sshve1_t30gms'] || 0);
                
                if (!grouped[cid]) {{
                    grouped[cid] = {{
                        team: team,
                        alias: alias,
                        sourced_gms: 0,
                        non_sourced_gms: 0
                    }};
                }}
                
                if (sourced === 'Y') {{
                    grouped[cid].sourced_gms += t30gms;
                }} else if (sourced === 'N') {{
                    grouped[cid].non_sourced_gms += t30gms;
                }}
            }});
            
            const tbody = document.getElementById('sourcingTableBody');
            tbody.innerHTML = '';
            
            // フィルター適用時のみデータを表示
            if (selectedTeam.length > 0 || selectedAlias.length > 0) {{
                Object.entries(grouped).forEach(([cid, data]) => {{
                    const total = data.sourced_gms + data.non_sourced_gms;
                    const sourcedPercent = total !== 0 ? (data.sourced_gms / total * 100) : 0;
                    
                    const row = document.createElement('tr');
                    row.innerHTML = `
                        <td>${{cid}}</td>
                        <td>${{data.team}}</td>
                        <td>${{data.alias}}</td>
                        <td class="number">${{data.sourced_gms.toLocaleString('en-US', {{minimumFractionDigits: 2, maximumFractionDigits: 2}})}}</td>
                        <td class="number">${{data.non_sourced_gms.toLocaleString('en-US', {{minimumFractionDigits: 2, maximumFractionDigits: 2}})}}</td>
                        <td class="number">${{total.toLocaleString('en-US', {{minimumFractionDigits: 2, maximumFractionDigits: 2}})}}</td>
                        <td class="number">${{sourcedPercent.toFixed(2)}}%</td>
                    `;
                    tbody.appendChild(row);
                }});
            }} else {{
                // フィルター未選択時はメッセージを表示
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td colspan="7" style="text-align: center; padding: 30px; color: #666;">
                        Team または Alias を選択してデータを表示してください
                    </td>
                `;
                tbody.appendChild(row);
            }}
        }}
    </script>
</body>
</html>'''
    
    return html


if __name__ == '__main__':
    if len(sys.argv) < 4:
        print("使用方法: python src/generate_standalone_dashboard.py <データファイル> <セラーリストファイル> <Top40Kファイル> [出力ファイル]")
        print("\n例:")
        print('  python src/generate_standalone_dashboard.py "C:\\Users\\murakei\\Desktop\\3PEITS_AI\\Opp_Dashboard\\raw\\Sourcing&Suppression_Sample.txt" "C:\\Users\\murakei\\Desktop\\3PEITS_AI\\Opp_Dashboard\\raw\\EITS_Seller_list.xlsx" "C:\\Users\\murakei\\Downloads\\3P_E&ITS_SS HVE#1_Top40K_Tracking_v6.xlsx"')
        sys.exit(1)
    
    data_file = sys.argv[1]
    seller_file = sys.argv[2]
    top40k_file = sys.argv[3]
    output_file = sys.argv[4] if len(sys.argv) > 4 else 'standalone_dashboard.html'
    
    generate_standalone_dashboard(data_file, seller_file, top40k_file, output_file)
