"""Webダッシュボード - Flaskアプリケーション"""

from flask import Flask, render_template, request, jsonify
import pandas as pd
from datetime import datetime
from pathlib import Path
import traceback


app = Flask(__name__, template_folder='../../templates')

# グローバル変数でデータを保持
current_data = None
seller_master = None


@app.route('/')
def index():
    """メインダッシュボードページ"""
    return render_template('data_dashboard.html')


@app.route('/api/load_data', methods=['POST'])
def load_data():
    """データファイルを読み込む"""
    global current_data, seller_master
    
    try:
        data = request.json
        data_file = data.get('data_file')
        seller_file = data.get('seller_file')
        
        if not data_file:
            return jsonify({
                'success': False,
                'error': 'データファイルパスは必須です'
            }), 400
        
        # データファイルを読み込み
        current_data = pd.read_csv(data_file, sep='\t', encoding='utf-8')
        
        # Sellerマスタを読み込み
        if seller_file:
            seller_master = pd.read_excel(seller_file)
            # merchant_customer_idでマージ
            if 'merchant_customer_id' in current_data.columns and 'merchant_customer_id' in seller_master.columns:
                current_data = current_data.merge(
                    seller_master[['merchant_customer_id', 'team', 'alias']], 
                    on='merchant_customer_id', 
                    how='left'
                )
                current_data['team'].fillna('Unknown', inplace=True)
                current_data['alias'].fillna('Unknown', inplace=True)
        
        # 基本統計を計算
        stats = {
            'total_rows': len(current_data),
            'total_columns': len(current_data.columns),
            'columns': current_data.columns.tolist()
        }
        
        # 数値列の統計
        numeric_cols = current_data.select_dtypes(include=['number']).columns.tolist()
        if numeric_cols:
            stats['numeric_summary'] = current_data[numeric_cols].describe().to_dict()
        
        return jsonify({
            'success': True,
            'stats': stats,
            'message': f'データを読み込みました（{len(current_data):,}行 × {len(current_data.columns)}列）'
        })
        
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


@app.route('/api/get_data', methods=['POST'])
def get_data():
    """フィルタリングされたデータを取得"""
    global current_data
    
    if current_data is None:
        return jsonify({
            'success': False,
            'error': 'データが読み込まれていません'
        }), 400
    
    try:
        filters = request.json.get('filters', {})
        
        # データをフィルタリング
        filtered_data = current_data.copy()
        
        for column, values in filters.items():
            if column in filtered_data.columns and values:
                filtered_data = filtered_data[filtered_data[column].isin(values)]
        
        # 最初の1000行を返す
        result_data = {
            'success': True,
            'columns': filtered_data.columns.tolist(),
            'data': filtered_data.head(1000).to_dict('records'),
            'total_rows': len(filtered_data),
            'filtered_rows': min(1000, len(filtered_data))
        }
        
        return jsonify(result_data)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'エラー: {str(e)}',
            'traceback': traceback.format_exc()
        }), 500


@app.route('/api/get_filter_options', methods=['GET'])
def get_filter_options():
    """フィルタ用のユニーク値を取得"""
    global current_data
    
    if current_data is None:
        return jsonify({
            'success': False,
            'error': 'データが読み込まれていません'
        }), 400
    
    try:
        # カテゴリカルな列のユニーク値を取得
        filter_columns = ['pf', 'gl', 'team', 'alias', 'suppression_status']
        options = {}
        
        for col in filter_columns:
            if col in current_data.columns:
                unique_values = current_data[col].dropna().unique().tolist()
                options[col] = sorted([str(v) for v in unique_values])
        
        return jsonify({
            'success': True,
            'options': options
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'エラー: {str(e)}'
        }), 500


def run_dashboard(host='127.0.0.1', port=5000, debug=False):
    """ダッシュボードを起動"""
    print(f"=" * 80)
    print(f"DataCentral Data Dashboard")
    print(f"=" * 80)
    print(f"ダッシュボードURL: http://{host}:{port}")
    print(f"ブラウザで上記URLを開いてください")
    print(f"=" * 80)
    app.run(host=host, port=port, debug=debug)
