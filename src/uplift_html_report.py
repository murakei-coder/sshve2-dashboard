"""
Uplift Interaction Analyzer - HTML Report Generator

HTMLレポート生成機能
- 視覚的にわかりやすいレポート
- 統計的有意性の解説
- グラフの埋め込み
"""

import base64
from pathlib import Path
from typing import List
from uplift_models import AnalysisResult, RegressionCoefficient


class HTMLReportGenerator:
    """HTMLレポートを生成するクラス"""
    
    def generate_report(self, result: AnalysisResult, output_path: str) -> str:
        """
        HTMLレポートを生成
        
        Args:
            result: 分析結果
            output_path: 出力ファイルパス
            
        Returns:
            str: 保存したファイルパス
        """
        html = self._build_html(result)
        
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(path, 'w', encoding='utf-8') as f:
            f.write(html)
        
        return str(path)
    
    def _build_html(self, result: AnalysisResult) -> str:
        """HTMLを構築"""
        reg = result.regression
        interp = result.interpretation
        
        # 係数を取得
        price_coef = next((c for c in reg.coefficients if c.name == 'our_price'), None)
        discount_coef = next((c for c in reg.coefficients if c.name == 'discount_percent'), None)
        interaction_coef = next((c for c in reg.coefficients if c.name == '交互作用項'), None)
        
        # グラフを埋め込み用に変換
        graphs_html = self._embed_graphs(result.figure_paths)
        
        html = f'''<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Uplift交互作用分析レポート</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ 
            font-family: 'Segoe UI', 'Meiryo', sans-serif; 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}
        .container {{ 
            max-width: 1200px; 
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
            text-align: center;
        }}
        .header h1 {{ font-size: 2.5em; margin-bottom: 10px; }}
        .header p {{ opacity: 0.8; font-size: 1.1em; }}
        .content {{ padding: 40px; }}
        .section {{ margin-bottom: 40px; }}
        .section-title {{
            font-size: 1.5em;
            color: #1a1a2e;
            border-left: 5px solid #667eea;
            padding-left: 15px;
            margin-bottom: 20px;
        }}
        .card {{
            background: #f8f9fa;
            border-radius: 15px;
            padding: 25px;
            margin-bottom: 20px;
        }}
        .card-title {{
            font-size: 1.2em;
            color: #333;
            margin-bottom: 15px;
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
        }}
        .stat-box {{
            background: white;
            border-radius: 10px;
            padding: 20px;
            text-align: center;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        .stat-value {{
            font-size: 2em;
            font-weight: bold;
            color: #667eea;
        }}
        .stat-label {{
            color: #666;
            margin-top: 5px;
        }}
        .coef-table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 15px;
        }}
        .coef-table th, .coef-table td {{
            padding: 15px;
            text-align: left;
            border-bottom: 1px solid #eee;
        }}
        .coef-table th {{
            background: #667eea;
            color: white;
        }}
        .coef-table tr:hover {{
            background: #f5f5f5;
        }}
        .significant {{ color: #28a745; font-weight: bold; }}
        .not-significant {{ color: #dc3545; }}
        .badge {{
            display: inline-block;
            padding: 5px 12px;
            border-radius: 20px;
            font-size: 0.85em;
            font-weight: bold;
        }}
        .badge-success {{ background: #d4edda; color: #155724; }}
        .badge-danger {{ background: #f8d7da; color: #721c24; }}
        .badge-warning {{ background: #fff3cd; color: #856404; }}
        .interpretation {{
            background: linear-gradient(135deg, #e8f4f8 0%, #d4e8f0 100%);
            border-radius: 15px;
            padding: 25px;
            margin-top: 20px;
        }}
        .interpretation h4 {{
            color: #1a1a2e;
            margin-bottom: 15px;
        }}
        .interpretation p {{
            line-height: 1.8;
            color: #333;
        }}
        .conclusion-box {{
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            color: white;
            border-radius: 15px;
            padding: 30px;
            margin-top: 30px;
        }}
        .conclusion-box h3 {{
            margin-bottom: 15px;
            font-size: 1.3em;
        }}
        .conclusion-box p {{
            line-height: 1.8;
            opacity: 0.9;
        }}
        .graph-container {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(500px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }}
        .graph-item {{
            background: white;
            border-radius: 10px;
            padding: 15px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        .graph-item img {{
            width: 100%;
            height: auto;
            border-radius: 5px;
        }}
        .explanation {{
            background: #fff9e6;
            border-left: 4px solid #ffc107;
            padding: 20px;
            margin: 20px 0;
            border-radius: 0 10px 10px 0;
        }}
        .explanation h4 {{
            color: #856404;
            margin-bottom: 10px;
        }}
        .explanation p {{
            color: #666;
            line-height: 1.7;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 Uplift交互作用分析レポート</h1>
            <p>価格と割引率がUpliftに与える影響の統計分析</p>
        </div>
        
        <div class="content">
            <!-- サマリー -->
            <div class="section">
                <h2 class="section-title">📈 分析サマリー</h2>
                <div class="stats-grid">
                    <div class="stat-box">
                        <div class="stat-value">{reg.n_observations:,}</div>
                        <div class="stat-label">分析対象レコード数</div>
                    </div>
                    <div class="stat-box">
                        <div class="stat-value">{reg.r_squared:.4f}</div>
                        <div class="stat-label">R²（決定係数）</div>
                    </div>
                    <div class="stat-box">
                        <div class="stat-value">{reg.f_statistic:.2f}</div>
                        <div class="stat-label">F統計量</div>
                    </div>
                    <div class="stat-box">
                        <div class="stat-value">{"✓" if interp.hypothesis_supported else "✗"}</div>
                        <div class="stat-label">仮説支持</div>
                    </div>
                </div>
            </div>
            
            <!-- 記述統計 -->
            <div class="section">
                <h2 class="section-title">📋 記述統計</h2>
                <div class="stats-grid">
                    {self._build_descriptive_stats_html(result.descriptive_stats)}
                </div>
            </div>
            
            <!-- 回帰分析結果 -->
            <div class="section">
                <h2 class="section-title">🔬 回帰分析結果</h2>
                
                <div class="card">
                    <div class="card-title">📊 係数一覧</div>
                    <table class="coef-table">
                        <thead>
                            <tr>
                                <th>変数</th>
                                <th>係数</th>
                                <th>標準誤差</th>
                                <th>t値</th>
                                <th>p値</th>
                                <th>有意性</th>
                            </tr>
                        </thead>
                        <tbody>
                            {self._build_coef_rows(reg.coefficients)}
                        </tbody>
                    </table>
                </div>
                
                <div class="explanation">
                    <h4>💡 統計的有意性とは？</h4>
                    <p>
                        p値が0.05未満の場合、その変数の効果は「統計的に有意」と判断されます。
                        これは、観測された効果が偶然によるものである確率が5%未満であることを意味します。
                        p値が小さいほど、その効果が本物である可能性が高くなります。
                    </p>
                </div>
            </div>
            
            <!-- 各変数の影響分析 -->
            <div class="section">
                <h2 class="section-title">📊 各変数のUpliftへの影響</h2>
                
                {self._build_variable_analysis(price_coef, 'our_price', '価格', '💰')}
                {self._build_variable_analysis(discount_coef, 'discount_percent', '割引率', '🏷️')}
                {self._build_interaction_analysis(interaction_coef)}
            </div>
            
            <!-- グラフ -->
            <div class="section">
                <h2 class="section-title">📈 視覚化</h2>
                <div class="graph-container">
                    {graphs_html}
                </div>
            </div>
            
            <!-- 結論 -->
            <div class="section">
                <h2 class="section-title">📝 結論</h2>
                <div class="conclusion-box">
                    <h3>{"✓ 仮説は支持されました" if interp.hypothesis_supported else "✗ 仮説は支持されませんでした"}</h3>
                    <p>{interp.conclusion}</p>
                </div>
                
                <div class="interpretation">
                    <h4>📌 ビジネスへの示唆</h4>
                    <p>
                        {self._build_business_implications(price_coef, discount_coef, interaction_coef, interp)}
                    </p>
                </div>
            </div>
        </div>
    </div>
</body>
</html>'''
        return html

    
    def _build_descriptive_stats_html(self, stats_list) -> str:
        """記述統計のHTMLを構築"""
        html = ""
        labels = {
            'our_price': ('💰 価格', '円'),
            'discount_percent_numeric': ('🏷️ 割引率', '%'),
            'uplift': ('📈 Uplift', '%')
        }
        
        for stats in stats_list:
            label, unit = labels.get(stats.variable, (stats.variable, ''))
            html += f'''
            <div class="stat-box">
                <div class="stat-label">{label}</div>
                <div class="stat-value">{stats.mean:,.1f}<small>{unit}</small></div>
                <div class="stat-label">
                    最小: {stats.min_val:,.1f} / 最大: {stats.max_val:,.1f}
                </div>
            </div>
            '''
        return html
    
    def _build_coef_rows(self, coefficients: List[RegressionCoefficient]) -> str:
        """係数テーブルの行を構築"""
        html = ""
        for coef in coefficients:
            sig_class = "significant" if coef.is_significant else "not-significant"
            sig_badge = "badge-success" if coef.is_significant else "badge-danger"
            sig_text = "有意 ✓" if coef.is_significant else "非有意"
            stars = "***" if coef.p_value < 0.001 else "**" if coef.p_value < 0.01 else "*" if coef.p_value < 0.05 else ""
            
            html += f'''
            <tr>
                <td><strong>{coef.name}</strong></td>
                <td>{coef.coefficient:.6f}</td>
                <td>{coef.std_error:.6f}</td>
                <td>{coef.t_value:.4f}</td>
                <td class="{sig_class}">{coef.p_value:.4e} {stars}</td>
                <td><span class="badge {sig_badge}">{sig_text}</span></td>
            </tr>
            '''
        return html
    
    def _build_variable_analysis(self, coef: RegressionCoefficient, var_name: str, display_name: str, icon: str) -> str:
        """各変数の分析HTMLを構築"""
        if coef is None:
            return ""
        
        direction = "正" if coef.coefficient > 0 else "負"
        effect_desc = "増加させる" if coef.coefficient > 0 else "減少させる"
        
        if coef.is_significant:
            significance_html = f'''
            <span class="badge badge-success">統計的に有意 (p={coef.p_value:.4e})</span>
            <p style="margin-top: 15px;">
                <strong>{display_name}が1単位増加すると、Upliftは平均{abs(coef.coefficient):.4f}%{effect_desc}傾向があります。</strong>
                この効果は統計的に有意であり、偶然ではなく実際の関係性を示している可能性が高いです。
            </p>
            '''
        else:
            significance_html = f'''
            <span class="badge badge-danger">統計的に有意ではない (p={coef.p_value:.4f})</span>
            <p style="margin-top: 15px;">
                {display_name}のUpliftへの影響は、このデータセットでは統計的に有意ではありませんでした。
                これは、{display_name}とUpliftの間に明確な関係が見られないか、
                サンプルサイズやデータのばらつきにより検出できなかった可能性があります。
            </p>
            '''
        
        return f'''
        <div class="card">
            <div class="card-title">{icon} {display_name}の影響</div>
            <div style="display: flex; gap: 20px; align-items: center; margin-bottom: 15px;">
                <div>
                    <strong>係数:</strong> {coef.coefficient:.6f}
                </div>
                <div>
                    <strong>効果の方向:</strong> {direction}の影響
                </div>
                {significance_html}
            </div>
        </div>
        '''
    
    def _build_interaction_analysis(self, coef: RegressionCoefficient) -> str:
        """交互作用効果の分析HTMLを構築"""
        if coef is None:
            return ""
        
        if coef.is_significant and coef.coefficient > 0:
            conclusion = '''
            <span class="badge badge-success">交互作用効果あり ✓</span>
            <p style="margin-top: 15px;">
                <strong>価格と割引率の交互作用効果は統計的に有意です。</strong>
                これは、価格が高い商品に対して高い割引率を適用すると、
                それぞれの効果の単純な合計以上のUplift効果が得られることを意味します。
                つまり、高価格帯の商品では、割引率を上げることでより大きなプロモーション効果が期待できます。
            </p>
            '''
        elif coef.is_significant and coef.coefficient < 0:
            conclusion = '''
            <span class="badge badge-warning">負の交互作用効果</span>
            <p style="margin-top: 15px;">
                <strong>価格と割引率の交互作用効果は統計的に有意ですが、負の方向です。</strong>
                これは、価格が高い商品に対して高い割引率を適用しても、
                期待されるほどのUplift効果が得られない可能性を示唆しています。
            </p>
            '''
        else:
            conclusion = f'''
            <span class="badge badge-danger">交互作用効果なし (p={coef.p_value:.4f})</span>
            <p style="margin-top: 15px;">
                <strong>価格と割引率の交互作用効果は統計的に有意ではありませんでした。</strong>
                これは、価格と割引率がそれぞれ独立してUpliftに影響を与えており、
                両方を組み合わせても相乗効果は見られないことを意味します。
                価格帯に関係なく、割引率の効果は一定である可能性があります。
            </p>
            '''
        
        return f'''
        <div class="card" style="background: linear-gradient(135deg, #fff5f5 0%, #ffe8e8 100%);">
            <div class="card-title">🔗 交互作用効果（価格 × 割引率）</div>
            <div style="display: flex; gap: 20px; align-items: center; margin-bottom: 15px;">
                <div>
                    <strong>係数:</strong> {coef.coefficient:.8f}
                </div>
                <div>
                    <strong>p値:</strong> {coef.p_value:.4f}
                </div>
            </div>
            {conclusion}
        </div>
        '''
    
    def _build_business_implications(self, price_coef, discount_coef, interaction_coef, interp) -> str:
        """ビジネスへの示唆を構築"""
        implications = []
        
        if price_coef and price_coef.is_significant:
            if price_coef.coefficient > 0:
                implications.append("高価格帯の商品はプロモーション効果が高い傾向があります。")
            else:
                implications.append("低価格帯の商品の方がプロモーション効果が高い傾向があります。")
        
        if discount_coef and discount_coef.is_significant:
            if discount_coef.coefficient > 0:
                implications.append(f"割引率を1%上げるごとに、Upliftは約{discount_coef.coefficient:.2f}%向上する傾向があります。")
        
        if interaction_coef:
            if interaction_coef.is_significant and interaction_coef.coefficient > 0:
                implications.append("高価格帯の商品に高い割引率を適用することで、より大きなプロモーション効果が期待できます。")
            elif not interaction_coef.is_significant:
                implications.append("価格帯に関係なく、割引率の効果は一定です。すべての価格帯で同様の割引戦略が有効です。")
        
        if not implications:
            implications.append("このデータセットからは明確なビジネス示唆を導き出すことが困難です。追加のデータや分析が必要かもしれません。")
        
        return "<br>".join([f"• {imp}" for imp in implications])
    
    def _embed_graphs(self, figure_paths: List[str]) -> str:
        """グラフをBase64エンコードして埋め込み"""
        html = ""
        titles = {
            'scatter': '散布図',
            'heatmap': 'ヒートマップ',
            'interaction': '交互作用プロット',
            'price': '価格 vs Uplift',
            'discount': '割引率 vs Uplift'
        }
        
        for path in figure_paths:
            try:
                with open(path, 'rb') as f:
                    img_data = base64.b64encode(f.read()).decode('utf-8')
                
                # タイトルを推測
                title = "グラフ"
                for key, val in titles.items():
                    if key in path.lower():
                        title = val
                        break
                
                html += f'''
                <div class="graph-item">
                    <h4 style="margin-bottom: 10px; color: #333;">{title}</h4>
                    <img src="data:image/png;base64,{img_data}" alt="{title}">
                </div>
                '''
            except Exception as e:
                html += f'<div class="graph-item"><p>グラフを読み込めませんでした: {path}</p></div>'
        
        return html
