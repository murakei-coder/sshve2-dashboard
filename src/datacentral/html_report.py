"""HTMLレポート生成コンポーネント"""

import pandas as pd
from datetime import datetime
from pathlib import Path


class HTMLReportGenerator:
    """クエリ結果をHTMLレポートとして生成"""
    
    def generate_report(self, df: pd.DataFrame, query: str, metadata: dict, output_path: str) -> str:
        """
        HTMLレポートを生成
        
        Parameters:
            df: クエリ結果のDataFrame
            query: 実行したクエリ
            metadata: メタデータ（URL、日付など）
            output_path: 出力ファイルパス
        
        Returns:
            保存したファイルパス
        """
        html = self._build_html(df, query, metadata)
        
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(path, 'w', encoding='utf-8') as f:
            f.write(html)
        
        return str(path)
    
    def _build_html(self, df: pd.DataFrame, query: str, metadata: dict) -> str:
        """HTMLを構築"""
        
        # 基本統計を計算
        stats_html = self._build_stats_html(df)
        
        # データテーブルを構築
        table_html = self._build_table_html(df)
        
        html = f'''<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>DataCentral Query Result</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ 
            font-family: 'Segoe UI', 'Meiryo', sans-serif; 
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
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
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
        .section {{ margin-bottom: 40px; }}
        .section-title {{
            font-size: 1.5em;
            color: #1a1a2e;
            border-left: 5px solid #667eea;
            padding-left: 15px;
            margin-bottom: 20px;
        }}
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        .stat-box {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border-radius: 15px;
            padding: 25px;
            text-align: center;
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.3);
        }}
        .stat-value {{
            font-size: 2.5em;
            font-weight: bold;
            margin-bottom: 5px;
        }}
        .stat-label {{
            opacity: 0.9;
            font-size: 0.9em;
        }}
        .query-box {{
            background: #f8f9fa;
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 30px;
            border-left: 4px solid #667eea;
        }}
        .query-box h3 {{
            color: #1a1a2e;
            margin-bottom: 15px;
        }}
        .query-text {{
            background: #1a1a2e;
            color: #00ff00;
            padding: 20px;
            border-radius: 8px;
            font-family: 'Courier New', monospace;
            font-size: 0.9em;
            overflow-x: auto;
            white-space: pre-wrap;
            word-wrap: break-word;
        }}
        .table-container {{
            background: white;
            border-radius: 10px;
            overflow: hidden;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        .data-table {{
            width: 100%;
            border-collapse: collapse;
        }}
        .data-table thead {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }}
        .data-table th {{
            padding: 15px;
            text-align: left;
            font-weight: 600;
            position: sticky;
            top: 0;
            z-index: 10;
        }}
        .data-table td {{
            padding: 12px 15px;
            border-bottom: 1px solid #eee;
        }}
        .data-table tbody tr:hover {{
            background: #f8f9fa;
        }}
        .data-table tbody tr:nth-child(even) {{
            background: #fafafa;
        }}
        .data-table tbody tr:nth-child(even):hover {{
            background: #f0f0f0;
        }}
        .filter-box {{
            background: white;
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        .filter-input {{
            width: 100%;
            padding: 12px;
            border: 2px solid #e0e0e0;
            border-radius: 8px;
            font-size: 1em;
            transition: border-color 0.3s;
        }}
        .filter-input:focus {{
            outline: none;
            border-color: #667eea;
        }}
        .no-data {{
            text-align: center;
            padding: 40px;
            color: #999;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 DataCentral Query Result</h1>
            <p>クエリ実行結果レポート</p>
            
            <div class="metadata">
                <div class="metadata-item">
                    <div class="metadata-label">実行日時</div>
                    <div class="metadata-value">{metadata.get('timestamp', 'N/A')}</div>
                </div>
                <div class="metadata-item">
                    <div class="metadata-label">URL</div>
                    <div class="metadata-value" style="font-size: 0.9em; word-break: break-all;">
                        {metadata.get('url', 'N/A')}
                    </div>
                </div>
                <div class="metadata-item">
                    <div class="metadata-label">置換日付</div>
                    <div class="metadata-value">{metadata.get('date', 'N/A')}</div>
                </div>
                <div class="metadata-item">
                    <div class="metadata-label">データベース</div>
                    <div class="metadata-value">{metadata.get('database', 'N/A')}</div>
                </div>
            </div>
        </div>
        
        <div class="content">
            <!-- 統計サマリー -->
            <div class="section">
                <h2 class="section-title">📈 データサマリー</h2>
                <div class="stats-grid">
                    {stats_html}
                </div>
            </div>
            
            <!-- 実行したクエリ -->
            <div class="section">
                <h2 class="section-title">🔍 実行したクエリ</h2>
                <div class="query-box">
                    <div class="query-text">{self._escape_html(query)}</div>
                </div>
            </div>
            
            <!-- データテーブル -->
            <div class="section">
                <h2 class="section-title">📋 クエリ結果（{len(df):,}行）</h2>
                
                <div class="filter-box">
                    <input type="text" 
                           id="searchInput" 
                           class="filter-input" 
                           placeholder="🔍 テーブル内を検索...">
                </div>
                
                <div class="table-container">
                    {table_html}
                </div>
            </div>
        </div>
    </div>
    
    <script>
        // テーブル検索機能
        document.getElementById('searchInput').addEventListener('keyup', function() {{
            const searchValue = this.value.toLowerCase();
            const table = document.querySelector('.data-table tbody');
            const rows = table.getElementsByTagName('tr');
            
            for (let i = 0; i < rows.length; i++) {{
                const row = rows[i];
                const text = row.textContent.toLowerCase();
                
                if (text.includes(searchValue)) {{
                    row.style.display = '';
                }} else {{
                    row.style.display = 'none';
                }}
            }}
        }});
    </script>
</body>
</html>'''
        return html
    
    def _build_stats_html(self, df: pd.DataFrame) -> str:
        """統計情報のHTMLを構築"""
        stats = []
        
        # 行数
        stats.append(f'''
        <div class="stat-box">
            <div class="stat-value">{len(df):,}</div>
            <div class="stat-label">総行数</div>
        </div>
        ''')
        
        # 列数
        stats.append(f'''
        <div class="stat-box">
            <div class="stat-value">{len(df.columns)}</div>
            <div class="stat-label">列数</div>
        </div>
        ''')
        
        # 数値列の統計
        numeric_cols = df.select_dtypes(include=['number']).columns
        if len(numeric_cols) > 0:
            stats.append(f'''
            <div class="stat-box">
                <div class="stat-value">{len(numeric_cols)}</div>
                <div class="stat-label">数値列</div>
            </div>
            ''')
        
        # 欠損値
        missing_count = df.isnull().sum().sum()
        stats.append(f'''
        <div class="stat-box">
            <div class="stat-value">{missing_count:,}</div>
            <div class="stat-label">欠損値</div>
        </div>
        ''')
        
        return '\n'.join(stats)
    
    def _build_table_html(self, df: pd.DataFrame) -> str:
        """データテーブルのHTMLを構築"""
        if len(df) == 0:
            return '<div class="no-data">データがありません</div>'
        
        # ヘッダー
        headers = ''.join([f'<th>{self._escape_html(str(col))}</th>' for col in df.columns])
        
        # 行（最大1000行まで表示）
        display_df = df.head(1000)
        rows = []
        for _, row in display_df.iterrows():
            cells = ''.join([f'<td>{self._escape_html(str(val))}</td>' for val in row])
            rows.append(f'<tr>{cells}</tr>')
        
        rows_html = '\n'.join(rows)
        
        # 1000行以上ある場合は注意書き
        note = ''
        if len(df) > 1000:
            note = f'<tr><td colspan="{len(df.columns)}" style="text-align: center; padding: 20px; background: #fff3cd; color: #856404;">最初の1,000行のみ表示しています（全{len(df):,}行）</td></tr>'
        
        return f'''
        <table class="data-table">
            <thead>
                <tr>{headers}</tr>
            </thead>
            <tbody>
                {rows_html}
                {note}
            </tbody>
        </table>
        '''
    
    def _escape_html(self, text: str) -> str:
        """HTMLエスケープ"""
        return (str(text)
                .replace('&', '&amp;')
                .replace('<', '&lt;')
                .replace('>', '&gt;')
                .replace('"', '&quot;')
                .replace("'", '&#39;'))
