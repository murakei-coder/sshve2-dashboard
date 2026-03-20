"""
GitHub Pages用の静的HTML版を生成
- データはJSONファイルから動的に読み込み
- あなたがJSONを更新すれば、営業担当はリロードするだけで最新データが見れる
"""

import json
from pathlib import Path
import re

def generate_static_html():
    """Generate static HTML for GitHub Pages."""
    
    # Read the template
    template_path = Path('templates/sshve2_dashboard.html')
    with open(template_path, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    # Remove Flask-specific links
    html_content = html_content.replace('<a href="/guide"', '<a href="guide.html"')
    
    # Replace API call with direct JSON loading
    api_call_pattern = r'\$\.ajax\(\{[^}]+url:\s*[\'"]\/api\/get_dashboard_data[\'"][^}]+\}\);'
    
    new_data_loading = """
// Load data from external JSON file
fetch('sshve2_data_new_suppression_20260318_222020.json')
.then(response => response.json())
.then(data => {
    ALL_DATA = data.cids;
    COEF = data.coefficients;
    SUPPRESSION_DATA = data.suppression_by_mcid || {};
    SSHVE1_AVG = data.sshve1_avg || {};
    initializeFilters();
    $('#timestamp').text(new Date().toLocaleString('ja-JP'));
    $('#resultsSection').html('<div class="empty"><h3>📋 フィルターを選択してください</h3></div>');
})
.catch(error => {
    console.error('データ読み込みエラー:', error);
    alert('データの読み込みに失敗しました。ページをリロードしてください。');
});
"""
    
    html_content = re.sub(api_call_pattern, new_data_loading, html_content, flags=re.DOTALL)
    
    # Remove download CSV API calls (not supported in static version)
    html_content = html_content.replace(
        '<a href="#" class="download-btn" onclick="downloadASINCSV(\'${cid.mcid}\'); return false;">📥 ASIN CSV</a>',
        '<!-- ASIN CSV download not available in static version -->'
    )
    
    # Remove /static/ prefix from script src
    html_content = html_content.replace('src="/static/dashboard.js"', 'src="dashboard.js"')
    
    # Write to index.html (GitHub Pages default)
    output_path = Path('index.html')
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"✅ 静的HTML生成完了: {output_path}")
    
    # Also copy guide template
    guide_path = Path('templates/sshve2_guide.html')
    if guide_path.exists():
        with open(guide_path, 'r', encoding='utf-8') as f:
            guide_content = f.read()
        
        # Remove Flask-specific links
        guide_content = guide_content.replace('<a href="/"', '<a href="index.html"')
        
        with open('guide.html', 'w', encoding='utf-8') as f:
            f.write(guide_content)
        
        print(f"✅ ガイドページ生成完了: guide.html")
    
    print()
    print("📝 次のステップ:")
    print("1. GitHub Desktopを開く")
    print("2. 変更をコミット（Summary: 'Add GitHub Pages static version'）")
    print("3. 'Push origin'をクリック")
    print("4. ブラウザで https://github.com/murakei-coder/sshve2-dashboard を開く")
    print("5. Settings → Pages → Source: main branch → Save")
    print("6. 1-2分待つ")
    print("7. https://murakei-coder.github.io/sshve2-dashboard/ にアクセス")
    print()
    print("💡 データ更新方法:")
    print("1. 新しいJSONファイルを生成")
    print("2. GitHub Desktopでコミット＆プッシュ")
    print("3. 営業担当はブラウザをリロード（F5）するだけ")

if __name__ == '__main__':
    generate_static_html()
