"""
Main script for Discount Effectiveness Analyzer.
Analyzes discount effectiveness and generates reports.
"""
import argparse
import logging
import sys
from pathlib import Path
from datetime import datetime

from src.discount_analyzer import (
    DataLoader, DataValidator, GrowthRateCalculator,
    PriceBandClassifier, DiscountAnalyzer, OptimalDiscountEstimator,
    ValidationError
)
from src.discount_models import AnalysisResults
from src.discount_report import HTMLReportGenerator, ExcelExporter, JSONSerializer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


def run_analysis(
    input_file: str,
    output_dir: str = None,
    output_prefix: str = None,
    use_gl: bool = False
) -> AnalysisResults:
    """
    Run discount effectiveness analysis.
    
    Args:
        input_file: Path to input data file
        output_dir: Directory for output files (default: same as input)
        output_prefix: Prefix for output files (default: based on input filename)
        use_gl: Whether to use GL column for analysis
        
    Returns:
        AnalysisResults object
    """
    input_path = Path(input_file)
    
    if not input_path.exists():
        raise FileNotFoundError(f"ファイルが見つかりません: {input_file}")
    
    # Set defaults
    if output_dir is None:
        output_dir = input_path.parent
    else:
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
    
    if output_prefix is None:
        output_prefix = input_path.stem
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    logger.info(f"=== 割引効果分析開始 ===")
    logger.info(f"入力ファイル: {input_file}")
    logger.info(f"GL分析モード: {'有効' if use_gl else '無効'}")
    
    # Step 1: Load data
    logger.info("Step 1: データ読み込み...")
    loader = DataLoader()
    df = loader.load(str(input_path))
    total_records = len(df)
    logger.info(f"  読み込み完了: {total_records:,}件")
    
    # Step 2: Validate data
    logger.info("Step 2: データバリデーション...")
    validator = DataValidator(use_gl=use_gl)
    validation_result = validator.validate(df)
    
    if not validation_result.is_valid:
        raise ValidationError(
            f"バリデーションエラー: {', '.join(validation_result.error_messages)}"
        )
    
    # Step 3: Clean data
    logger.info("Step 3: データクリーニング...")
    df = validator.clean(df)
    valid_records = len(df)
    logger.info(f"  有効レコード: {valid_records:,}件 (除外: {total_records - valid_records:,}件)")
    
    if valid_records == 0:
        raise ValueError("有効なデータがありません")
    
    # Step 4: Calculate growth rate
    logger.info("Step 4: 売上伸び率計算...")
    calculator = GrowthRateCalculator()
    df = calculator.calculate(df)
    
    # Step 5: Classify price bands and discount tiers
    logger.info("Step 5: 価格帯・割引率帯分類...")
    classifier = PriceBandClassifier()
    df = classifier.classify(df)
    
    # Step 6: Analyze by segment
    logger.info("Step 6: セグメント別分析...")
    analyzer = DiscountAnalyzer()
    
    # Analyze by PF
    analysis_results_pf = analyzer.analyze(df, group_by='pf')
    
    # Analyze by GL if available
    analysis_results_gl = []
    gl_price_discount_df = None
    if use_gl and 'gl' in df.columns:
        analysis_results_gl = analyzer.analyze(df, group_by='gl')
        gl_price_discount_df = analyzer.analyze_by_gl_price_discount(df)
        logger.info(f"  GL×価格帯×割引率: {len(gl_price_discount_df)}パターン")
    
    # Combine results
    analysis_results = analysis_results_pf + analysis_results_gl
    
    # Step 7: Estimate optimal discounts
    logger.info("Step 7: 最適割引率推定...")
    estimator = OptimalDiscountEstimator()
    recommendations = estimator.estimate(analysis_results)
    
    # Create results object
    results = AnalysisResults.create(
        raw_data_path=str(input_path),
        total_records=total_records,
        valid_records=valid_records
    )
    results.segment_analyses = analysis_results
    results.recommendations = recommendations
    
    # Step 8: Generate outputs
    logger.info("Step 8: レポート生成...")
    
    # HTML Report
    html_path = output_dir / f"{output_prefix}_analysis_{timestamp}.html"
    html_generator = HTMLReportGenerator()
    html_generator.generate(df, analysis_results, recommendations, str(html_path), gl_price_discount_df, str(input_path))
    
    # Excel Report
    excel_path = output_dir / f"{output_prefix}_analysis_{timestamp}.xlsx"
    excel_exporter = ExcelExporter()
    excel_exporter.export(df, analysis_results, recommendations, str(excel_path), gl_price_discount_df)
    
    # JSON (for later use)
    json_path = output_dir / f"{output_prefix}_analysis_{timestamp}.json"
    json_serializer = JSONSerializer()
    json_serializer.save(results, str(json_path))
    
    logger.info(f"=== 分析完了 ===")
    logger.info(f"HTMLレポート: {html_path}")
    logger.info(f"Excelファイル: {excel_path}")
    logger.info(f"JSONファイル: {json_path}")
    
    return results


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='割引効果分析ツール - PF/GL×価格帯ごとに最適割引率を分析'
    )
    parser.add_argument(
        'input_file',
        help='入力データファイルパス（タブ区切り）'
    )
    parser.add_argument(
        '-o', '--output-dir',
        help='出力ディレクトリ（デフォルト: 入力ファイルと同じ）'
    )
    parser.add_argument(
        '-p', '--prefix',
        help='出力ファイル名のプレフィックス'
    )
    parser.add_argument(
        '--gl', action='store_true',
        help='GL列を使用した分析を有効にする'
    )
    
    args = parser.parse_args()
    
    try:
        results = run_analysis(
            input_file=args.input_file,
            output_dir=args.output_dir,
            output_prefix=args.prefix,
            use_gl=args.gl
        )
        
        # Print summary
        print("\n" + "=" * 50)
        print("分析サマリー")
        print("=" * 50)
        print(f"総レコード数: {results.total_records:,}")
        print(f"有効レコード数: {results.valid_records:,}")
        print(f"除外レコード数: {results.excluded_records:,}")
        print(f"分析セグメント数: {len(results.segment_analyses)}")
        
        return 0
        
    except FileNotFoundError as e:
        logger.error(f"ファイルエラー: {e}")
        return 1
    except ValidationError as e:
        logger.error(f"バリデーションエラー: {e}")
        return 1
    except Exception as e:
        logger.error(f"エラーが発生しました: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
