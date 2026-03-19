"""
Sourcing Data Aggregator - メインスクリプト

CSVファイルからソーシングデータを読み込み、MCID単位で集約してレポートを生成する。

使用方法:
    python src/run_sourcing_aggregator.py <入力ファイル> [出力ディレクトリ]
"""

import sys
import argparse
import logging
from pathlib import Path
from datetime import datetime

from src.sourcing_aggregator import (
    CSVLoader,
    DataValidator,
    MCIDAggregator,
    ExcelExporter,
    CSVExporter
)


# ロギング設定（日本語メッセージ）
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


def run_aggregation(input_file: str, output_dir: str = None) -> None:
    """
    ソーシングデータの集約処理を実行
    
    Args:
        input_file: 入力CSVファイルパス
        output_dir: 出力ディレクトリ（省略時は入力ファイルと同じディレクトリ）
    """
    input_path = Path(input_file)
    
    # 入力ファイルの存在確認
    if not input_path.exists():
        raise FileNotFoundError(f"ファイルが見つかりません: {input_file}")
    
    # 出力ディレクトリの設定
    if output_dir is None:
        output_dir = input_path.parent
    else:
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
    
    logger.info("=" * 80)
    logger.info("ソーシングデータ集約処理を開始します")
    logger.info("=" * 80)
    logger.info(f"入力ファイル: {input_file}")
    logger.info(f"出力ディレクトリ: {output_dir}")
    
    # ステップ1: CSVファイル読み込み
    logger.info("\n[1/5] CSVファイルを読み込んでいます...")
    loader = CSVLoader()
    try:
        df = loader.load(str(input_path))
        logger.info(f"  ✓ 読み込み完了: {len(df):,}行")
    except FileNotFoundError as e:
        logger.error(f"  ✗ エラー: {e}")
        raise
    except UnicodeDecodeError as e:
        logger.error(f"  ✗ エンコーディングエラー: ファイルの文字コードを確認してください")
        raise
    
    # ステップ2: データバリデーション
    logger.info("\n[2/5] データを検証しています...")
    validator = DataValidator()
    validation_result = validator.validate(df)
    
    if not validation_result.is_valid:
        logger.error(f"  ✗ バリデーションエラー:")
        for error_msg in validation_result.error_messages:
            logger.error(f"    - {error_msg}")
        raise ValueError("データバリデーションに失敗しました")
    
    logger.info(f"  ✓ バリデーション成功: {validation_result.total_rows:,}行")
    
    # ステップ3: データクリーニング
    logger.info("\n[3/5] データをクリーニングしています...")
    original_count = len(df)
    df = validator.clean(df)
    cleaned_count = len(df)
    removed_count = original_count - cleaned_count
    
    if removed_count > 0:
        logger.warning(f"  ! {removed_count:,}行を除外しました（MCID欠損値）")
    logger.info(f"  ✓ クリーニング完了: {cleaned_count:,}行")
    
    if cleaned_count == 0:
        logger.error("  ✗ エラー: 有効なデータがありません")
        raise ValueError("有効なデータがありません")
    
    # ステップ4: MCID単位で集約
    logger.info("\n[4/5] MCID単位でデータを集約しています...")
    aggregator = MCIDAggregator()
    results = aggregator.aggregate(df)
    logger.info(f"  ✓ 集約完了: {len(results)}件のMCID")
    
    # ステップ5: レポート生成
    logger.info("\n[5/5] レポートを生成しています...")
    
    # Excelファイル生成
    excel_filename = "SS2_Sourcing_Status_BySeller.xlsx"
    excel_path = output_dir / excel_filename
    excel_exporter = ExcelExporter()
    excel_exporter.export(results, str(excel_path))
    logger.info(f"  ✓ Excelファイル: {excel_path}")
    
    # CSVファイル生成
    csv_filename = "SS2_Sourcing_Status_BySeller.csv"
    csv_path = output_dir / csv_filename
    csv_exporter = CSVExporter()
    csv_exporter.export(results, str(csv_path))
    logger.info(f"  ✓ CSVファイル: {csv_path}")
    
    # 完了メッセージ
    logger.info("\n" + "=" * 80)
    logger.info("✓ すべての処理が完了しました")
    logger.info("=" * 80)
    logger.info(f"Excelファイル: {excel_path}")
    logger.info(f"CSVファイル: {csv_path}")
    logger.info(f"集約結果: {len(results)}件のMCID")
    logger.info("=" * 80)


def main():
    """メイン関数"""
    parser = argparse.ArgumentParser(
        description='ソーシングデータ集約ツール - MCID単位でデータを集約してレポートを生成',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用例:
  python src/run_sourcing_aggregator.py data/sourcing_data.csv
  python src/run_sourcing_aggregator.py data/sourcing_data.csv -o output
  python src/run_sourcing_aggregator.py "C:\\data\\sourcing_data.csv" -o "C:\\output"
        """
    )
    
    parser.add_argument(
        'input_file',
        help='入力CSVファイルパス'
    )
    
    parser.add_argument(
        '-o', '--output-dir',
        default=None,
        help='出力ディレクトリ（デフォルト: 入力ファイルと同じディレクトリ）'
    )
    
    args = parser.parse_args()
    
    try:
        run_aggregation(
            input_file=args.input_file,
            output_dir=args.output_dir
        )
        return 0
        
    except FileNotFoundError as e:
        logger.error(f"\n✗ ファイルエラー: {e}")
        return 1
    
    except ValueError as e:
        logger.error(f"\n✗ データエラー: {e}")
        return 1
    
    except UnicodeDecodeError as e:
        logger.error(f"\n✗ エンコーディングエラー: ファイルの文字コードを確認してください")
        return 1
    
    except Exception as e:
        logger.error(f"\n✗ 予期しないエラーが発生しました: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
