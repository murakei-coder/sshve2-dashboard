"""データ分析ダッシュボード - Flaskアプリケーション"""

from flask import Flask, render_template, request, jsonify
import pandas as pd
from datetime import datetime
import traceback


app = Flask(__name__, template_folder='../../templates')


@app.route('/')
def index():
    """メインダッシュボードページ"""
    return render_template('data_dashboard.html')


@app.route('/api/load_data', methods=['POST'])
def load_data():
    """データファイルを読み込んで分析"""
    try:
        data = request.json
        data_file = data.get('data_file')
        seller_file = data.get('seller_file')
        
        if not data_file or not seller_file:
            return jsonify({
                'success': False,
                'error': 'データファイルとセラーリストファイルは必須です'
            }), 400
        
        # データファイルを読み込み
        df = pd.read_csv(data_file, sep='\t', encoding='utf-8')
        
        # セラーリストを読み込み
        seller_df = pd.read_excel(seller_file)
        
        # データを結合（merchant_customer_idをキーに）
        if 'merchant_customer_id' in df.columns and 'merchant_customer_id' in seller_df.columns:
            df = df.merge(seller_df[['merchant_customer_id', 'team', 'alias']], 
                         on='merchant_customer_id', 
                         how='left')
            df['team'] = df['team'].fillna('Unknown')
            df['alias'] = df['alias'].fillna('Unknown')
        
        # 基本統計を計算
        stats = {
            'total_rows': len(df),
            'total_columns': len(df.columns),
            'columns': df.columns.tolist()
        }
        
        # PF、GL、Team、Aliasのユニーク値を取得
        filters = {}
        if 'pf' in df.columns:
            filters['pf'] = df['pf'].unique().tolist()
        if 'gl' in df.columns:
            filters['gl'] = df['gl'].unique().tolist()
        if 'team' in df.columns:
            filters['team'] = df['team'].unique().tolist()
        if 'alias' in df.columns:
            filters['alias'] = df['alias'].unique().tolist()
        if 'suppression_status' in df.columns:
            filters['suppression_status'] = df['suppression_status'].unique().tolist()
        
        # データをJSON形式に変換（最初の1000行）
        result_data = {
            'success': True,
            'stats': stats,
            'filters': filters,
            'data': df.head(1000).to_dict('records'),
            'metadata': {
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'data_file': data_file,
                'seller_file': seller_file
            }
        }
        
        return jsonify(result_data)
        
    except FileNotFoundError as e:
        return jsonify({
            'success': False,
            'error': f'ファイルが見つかりません: {str(e)}'
        }), 400
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'エラー: {str(e)}',
            'traceback': traceback.format_exc()
        }), 500


@app.route('/api/filter_data', methods=['POST'])
def filter_data():
    """データをフィルタリング"""
    try:
        data = request.json
        data_file = data.get('data_file')
        seller_file = data.get('seller_file')
        filters = data.get('filters', {})
        
        # データを再読み込み
        df = pd.read_csv(data_file, sep='\t', encoding='utf-8')
        seller_df = pd.read_excel(seller_file)
        
        # データを結合
        if 'merchant_customer_id' in df.columns and 'merchant_customer_id' in seller_df.columns:
            df = df.merge(seller_df[['merchant_customer_id', 'team', 'alias']], 
                         on='merchant_customer_id', 
                         how='left')
            df['team'] = df['team'].fillna('Unknown')
            df['alias'] = df['alias'].fillna('Unknown')
        
        # フィルタを適用
        for key, values in filters.items():
            if values and key in df.columns:
                df = df[df[key].isin(values)]
        
        # 結果を返す
        result_data = {
            'success': True,
            'total_rows': len(df),
            'data': df.head(1000).to_dict('records')
        }
        
        return jsonify(result_data)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'エラー: {str(e)}'
        }), 500


def run_dashboard(host='127.0.0.1', port=5000, debug=False):
    """ダッシュボードを起動"""
    print(f"=" * 80)
    print(f"Data Analysis Dashboard")
    print(f"=" * 80)
    print(f"ダッシュボードURL: http://{host}:{port}")
    print(f"ブラウザで上記URLを開いてください")
    print(f"=" * 80)
    app.run(host=host, port=port, debug=debug)
