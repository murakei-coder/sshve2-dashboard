"""
SSHVE2 Opportunity Dashboard - Web Application
ブラウザでアクセスできるWebアプリ版
- ASIN単位のCSVダウンロード機能付き
- 使い方ガイド統合
"""

from flask import Flask, render_template, request, jsonify, send_file, Response
import json
import pandas as pd
from datetime import datetime
from pathlib import Path
import io
import traceback

app = Flask(__name__, template_folder='../templates')

# Global variables to cache loaded data
cached_data = {
    'cids_data': None,
    'coefficients': None,
    'suppression_by_mcid': None,
    'sshve1_avg': None,
    'raw_suppression_df': None,
    'last_loaded': None
}


def load_data():
    """Load all data files and cache them."""
    try:
        # Load JSON data
        json_file = 'sshve2_data_new_suppression_20260318_222020.json'
        print(f"Loading: {json_file}")
        
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Load raw suppression data (optimized version)
        suppression_file = r'C:\Users\murakei\Desktop\SSHVE2\Dashboard\raw\Suppression\SSHVE2_ByASIN_Suppression_raw_Final.txt'
        print(f"Loading raw suppression data: {suppression_file}")
        
        # Read with chunking for large files
        df_suppression = pd.read_csv(suppression_file, sep='\t', encoding='utf-8', low_memory=False)
        print(f"Loaded {len(df_suppression)} rows")
        
        # Pre-aggregate by MCID (fully optimized - no iteration)
        print("Aggregating by MCID...")
        
        # Single groupby operation - much faster than nested loops
        agg_result = df_suppression.groupby(['merchant_customer_id', 'suppression_category_large'])['t30d_ops'].sum()
        
        # Convert to nested dictionary structure
        suppression_by_mcid = {}
        for (mcid, category), ops_value in agg_result.items():
            mcid_str = str(mcid)
            if mcid_str not in suppression_by_mcid:
                suppression_by_mcid[mcid_str] = {}
            suppression_by_mcid[mcid_str][category] = ops_value
        
        print(f"Aggregated {len(suppression_by_mcid)} MCIDs")
        
        # Cache data
        cached_data['cids_data'] = data['cids']
        cached_data['coefficients'] = data['coefficients']
        cached_data['suppression_by_mcid'] = suppression_by_mcid
        cached_data['sshve1_avg'] = data.get('sshve1_avg', {})
        cached_data['raw_suppression_df'] = df_suppression
        cached_data['last_loaded'] = datetime.now()
        
        return True, f"データ読み込み成功: {len(data['cids'])} MCIDs"
    
    except Exception as e:
        traceback.print_exc()
        return False, f"データ読み込みエラー: {str(e)}"


@app.route('/')
def index():
    """Main dashboard page."""
    return render_template('sshve2_dashboard.html')


@app.route('/guide')
def guide():
    """Usage guide page."""
    return render_template('sshve2_guide.html')


@app.route('/api/get_dashboard_data', methods=['GET'])
def api_get_dashboard_data():
    """Get all dashboard data."""
    if cached_data['cids_data'] is None:
        return jsonify({'success': False, 'message': 'データが読み込まれていません'})
    
    try:
        return jsonify({
            'success': True,
            'data': {
                'cids': cached_data['cids_data'],
                'coefficients': cached_data['coefficients'],
                'suppression_by_mcid': cached_data['suppression_by_mcid'],
                'sshve1_avg': cached_data['sshve1_avg']
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})


@app.route('/api/download_asin_csv/<mcid>', methods=['GET'])
def api_download_asin_csv(mcid):
    """Download ASIN-level CSV for a specific MCID."""
    if cached_data['raw_suppression_df'] is None:
        return jsonify({'success': False, 'message': 'データが読み込まれていません'})
    
    try:
        df = cached_data['raw_suppression_df']
        
        # Filter by MCID
        mcid_data = df[df['merchant_customer_id'] == int(mcid)].copy()
        
        if mcid_data.empty:
            return jsonify({'success': False, 'message': f'MCID {mcid} のデータが見つかりません'})
        
        # Select relevant columns
        columns_to_export = [
            'merchant_customer_id',
            'merchant_name',
            'asin',
            'product_title',
            'suppression_category_large',
            't30d_gms',
            't30d_ops',
            'sshve2_sourced_flag'
        ]
        
        export_df = mcid_data[columns_to_export].copy()
        
        # Rename columns for clarity
        export_df.columns = [
            'MCID',
            'Merchant Name',
            'ASIN',
            'Product Title',
            'Suppression Category',
            'T30 GMS',
            'T30 OPS',
            'SSHVE2 Sourced'
        ]
        
        # Create CSV in memory with UTF-8 BOM
        output = io.StringIO()
        export_df.to_csv(output, index=False, encoding='utf-8-sig')
        output.seek(0)
        
        # Create response
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'SSHVE2_ASIN_Detail_MCID_{mcid}_{timestamp}.csv'
        
        return Response(
            output.getvalue(),
            mimetype='text/csv',
            headers={'Content-Disposition': f'attachment; filename={filename}'}
        )
    
    except Exception as e:
        traceback.print_exc()
        return jsonify({'success': False, 'message': f'エラー: {str(e)}'})


@app.route('/api/download_asin_csv_filtered/<mcid>/<category>', methods=['GET'])
def api_download_asin_csv_filtered(mcid, category):
    """Download ASIN-level CSV filtered by Sourcing/Suppression category."""
    if cached_data['raw_suppression_df'] is None:
        return jsonify({'success': False, 'message': 'データが読み込まれていません'})
    
    try:
        df = cached_data['raw_suppression_df']
        
        # Filter by MCID
        mcid_data = df[df['merchant_customer_id'] == int(mcid)].copy()
        
        if mcid_data.empty:
            return jsonify({'success': False, 'message': f'MCID {mcid} のデータが見つかりません'})
        
        # Filter by category
        if category == 'sourcing':
            # Sourcing: SSHVE2 Sourced = Y
            filtered_data = mcid_data[mcid_data['sshve2_sourced_flag'] == 'Y'].copy()
            category_name = 'Sourcing'
        elif category == 'suppression':
            # Suppression: All suppression categories except "1.no suppression"
            filtered_data = mcid_data[mcid_data['suppression_category_large'] != '1.no suppression'].copy()
            category_name = 'Suppression'
        else:
            return jsonify({'success': False, 'message': f'無効なカテゴリ: {category}'})
        
        if filtered_data.empty:
            return jsonify({'success': False, 'message': f'{category_name}のデータが見つかりません'})
        
        # Select relevant columns
        columns_to_export = [
            'merchant_customer_id',
            'merchant_name',
            'asin',
            'product_title',
            'suppression_category_large',
            't30d_gms',
            't30d_ops',
            'sshve2_sourced_flag'
        ]
        
        export_df = filtered_data[columns_to_export].copy()
        
        # Rename columns
        export_df.columns = [
            'MCID',
            'Merchant Name',
            'ASIN',
            'Product Title',
            'Suppression Category',
            'T30 GMS',
            'T30 OPS',
            'SSHVE2 Sourced'
        ]
        
        # Create CSV in memory with UTF-8 BOM
        output = io.StringIO()
        export_df.to_csv(output, index=False, encoding='utf-8-sig')
        output.seek(0)
        
        # Create response
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'SSHVE2_ASIN_{category_name}_MCID_{mcid}_{timestamp}.csv'
        
        return Response(
            output.getvalue(),
            mimetype='text/csv',
            headers={'Content-Disposition': f'attachment; filename={filename}'}
        )
    
    except Exception as e:
        traceback.print_exc()
        return jsonify({'success': False, 'message': f'エラー: {str(e)}'})


# Auto-load data on startup
print("=" * 80)
print("SSHVE2 Opportunity Dashboard - Web Application")
print("=" * 80)
print()
print("📂 データを読み込んでいます...")

success, message = load_data()
if success:
    print(f"✅ {message}")
else:
    print(f"❌ {message}")
    print("⚠️  データ読み込みに失敗しましたが、アプリは起動します")

print("=" * 80)

if __name__ == '__main__':
    print()
    print("🌐 開発モードで起動中...")
    print("   http://localhost:5001")
    print()
    print("⚠️  終了するには Ctrl+C を押してください")
    print("=" * 80)
    print()
    
    app.run(debug=True, host='0.0.0.0', port=5001)
