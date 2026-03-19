"""Webダッシュボードを起動するスクリプト"""

import sys
import webbrowser
import time
from threading import Timer

from datacentral.data_dashboard import run_dashboard


def open_browser():
    """ブラウザを開く"""
    webbrowser.open('http://127.0.0.1:5000')


if __name__ == '__main__':
    print("=" * 80)
    print("Data Analysis Dashboard 起動中...")
    print("=" * 80)
    
    # 1秒後にブラウザを開く
    Timer(1.0, open_browser).start()
    
    # ダッシュボードを起動
    run_dashboard(host='127.0.0.1', port=5000, debug=False)
