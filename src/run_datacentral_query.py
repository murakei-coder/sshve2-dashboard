"""DataCentral Query Executor - メインCLIスクリプト"""

import sys
import argparse
import webbrowser
from pathlib import Path
from datetime import datetime

# datacentral モジュールをインポート
from datacentral.query_fetcher import QueryFetcher
from datacentral.date_replacer import DateReplacer
from datacentral.query_executor import QueryExecutor
from datacentral.html_report import HTMLReportGenerator
from datacentral.exceptions import DataCentralError, QueryExecutionError, DataValidationError


def main():
    """メイン処理"""
    parser = argparse.ArgumentParser(
        description='DataCentralからクエリを取得し、日付を書き換えてローカルで実行',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用例:
  python src/run_datacentral_query.py --url "https://datacentral.a2z.com/..." --date 2026-02-02
  python src/run_datacentral_query.py --url "https://datacentral.a2z.com/..." --date 2026-02-02 --output results.txt
  python src/run_datacentral_query.py --url "https://datacentral.a2z.com/..." --date 2026-02-02 --db custom.sqlite
        """
    )
    
    parser.add_argument(
        '--url',
        required=True,
        help='DataCentral URL（例: https://datacentral.a2z.com/dw-platform/servlet/dwp/template/EtlViewExtractJobs.vm/job_profile_id/14164725）'
    )
    
    parser.add_argument(
        '--date',
        required=True,
        help='置換する日付（yyyy-mm-dd形式、例: 2026-02-02）'
    )
    
    parser.add_argument(
        '--output',
        default=None,
        help='結果を保存するファイルパス（デフォルト: query_result_YYYYMMDD_HHMMSS.txt）'
    )
    
    parser.add_argument(
        '--html',
        action='store_true',
        help='HTMLレポートを生成する'
    )
    
    parser.add_argument(
        '--html-output',
        default=None,
        help='HTMLレポートの出力パス（デフォルト: query_result_YYYYMMDD_HHMMSS.html）'
    )
    
    parser.add_argument(
        '--open-browser',
        action='store_true',
        help='HTMLレポート生成後、自動的にブラウザで開く'
    )
    
    parser.add_argument(
        '--db',
        default='database.sqlite',
        help='SQLiteデータベースファイルパス（デフォルト: database.sqlite）'
    )
    
    parser.add_argument(
        '--start-line',
        type=int,
        default=6,
        help='日付置換の開始行（デフォルト: 6）'
    )
    
    parser.add_argument(
        '--end-line',
        type=int,
        default=11,
        help='日付置換の終了行（デフォルト: 11）'
    )
    
    args = parser.parse_args()
    
    try:
        # ステップ1: クエリ取得
        print(f"[1/4] DataCentralからクエリを取得中...")
        print(f"  URL: {args.url}")
        fetcher = QueryFetcher()
        query = fetcher.fetch_query(args.url)
        print(f"  ✓ クエリを取得しました（{len(query)}文字）")
        
        # ステップ2: 日付置換
        print(f"\n[2/4] 日付を置換中...")
        print(f"  対象日付: {args.date}")
        print(f"  対象行: {args.start_line}～{args.end_line}行目")
        replacer = DateReplacer()
        modified_query = replacer.replace_dates(
            query, 
            args.date, 
            args.start_line, 
            args.end_line
        )
        print(f"  ✓ 日付を置換しました")
        
        # ステップ3: クエリ実行
        print(f"\n[3/4] ローカルデータベースでクエリを実行中...")
        print(f"  データベース: {args.db}")
        with QueryExecutor(args.db) as executor:
            result_df = executor.execute_query(modified_query)
        print(f"  ✓ クエリを実行しました（{len(result_df)}行 × {len(result_df.columns)}列）")
        
        # ステップ4: 結果を保存
        print(f"\n[4/4] 結果を保存中...")
        
        # 出力ファイル名を決定
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        if args.output:
            output_path = args.output
        else:
            output_path = f"query_result_{timestamp}.txt"
        
        # 結果をテキストファイルに保存
        with open(output_path, 'w', encoding='utf-8') as f:
            # ヘッダー情報
            f.write("=" * 80 + "\n")
            f.write("DataCentral Query Executor - 実行結果\n")
            f.write("=" * 80 + "\n")
            f.write(f"実行日時: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"URL: {args.url}\n")
            f.write(f"置換日付: {args.date}\n")
            f.write(f"データベース: {args.db}\n")
            f.write(f"結果行数: {len(result_df)}\n")
            f.write(f"結果列数: {len(result_df.columns)}\n")
            f.write("=" * 80 + "\n\n")
            
            # 実行したクエリ
            f.write("【実行したクエリ】\n")
            f.write("-" * 80 + "\n")
            f.write(modified_query)
            f.write("\n" + "-" * 80 + "\n\n")
            
            # 結果データ
            f.write("【実行結果】\n")
            f.write("-" * 80 + "\n")
            f.write(result_df.to_string(index=False))
            f.write("\n" + "-" * 80 + "\n")
        
        print(f"  ✓ テキストファイルを保存しました: {output_path}")
        
        # HTMLレポートを生成
        html_path = None
        if args.html:
            if args.html_output:
                html_path = args.html_output
            else:
                html_path = f"query_result_{timestamp}.html"
            
            print(f"  HTMLレポートを生成中...")
            html_generator = HTMLReportGenerator()
            metadata = {
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'url': args.url,
                'date': args.date,
                'database': args.db
            }
            html_generator.generate_report(result_df, modified_query, metadata, html_path)
            print(f"  ✓ HTMLレポートを保存しました: {html_path}")
            
            # ブラウザで開く
            if args.open_browser:
                print(f"  ブラウザでHTMLレポートを開いています...")
                abs_path = Path(html_path).resolve()
                webbrowser.open(f'file:///{abs_path}')
                print(f"  ✓ ブラウザで開きました")
        
        # 成功メッセージ
        print(f"\n{'='*80}")
        print(f"✓ すべての処理が完了しました")
        print(f"{'='*80}")
        print(f"テキストファイル: {output_path}")
        if html_path:
            print(f"HTMLレポート: {html_path}")
            abs_html_path = Path(html_path).resolve()
            print(f"ブラウザで開く: file:///{abs_html_path}")
        print(f"行数: {len(result_df)}")
        print(f"列数: {len(result_df.columns)}")
        
        return 0
        
    except DataCentralError as e:
        print(f"\n✗ DataCentralエラー: {str(e)}", file=sys.stderr)
        return 1
    
    except DataValidationError as e:
        print(f"\n✗ データ検証エラー: {str(e)}", file=sys.stderr)
        return 1
    
    except QueryExecutionError as e:
        print(f"\n✗ クエリ実行エラー: {str(e)}", file=sys.stderr)
        return 1
    
    except Exception as e:
        print(f"\n✗ 予期しないエラー: {str(e)}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
