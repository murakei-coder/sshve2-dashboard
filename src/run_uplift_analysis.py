"""
Uplift Interaction Analyzer - Main Script

価格と割引率がUpliftに与える影響を分析するメインスクリプト
特に交互作用効果（両方が高い場合にUpliftがさらに大きくなるか）を検証

使用方法:
    python run_uplift_analysis.py <ファイルパス> [出力ディレクトリ]
"""

import sys
import os
from pathlib import Path
from datetime import datetime

# srcディレクトリをパスに追加
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from uplift_data_loader import DataLoader, MissingColumnError
from uplift_data_processor import DataProcessor
from uplift_calculator import UpliftCalculator
from uplift_statistical_analyzer import StatisticalAnalyzer
from uplift_visualizer import Visualizer
from uplift_report_generator import ReportGenerator
from uplift_html_report import HTMLReportGenerator
from uplift_models import AnalysisResult


def run_analysis(file_path: str, output_dir: str = None) -> AnalysisResult:
    """
    Uplift交互作用分析を実行
    
    Args:
        file_path: 入力ファイルパス
        output_dir: 出力ディレクトリ（省略時はファイルと同じディレクトリ）
        
    Returns:
        AnalysisResult: 分析結果
    """
    # 出力ディレクトリの設定
    if output_dir is None:
        output_dir = str(Path(file_path).parent)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    print(f"\n分析を開始します...")
    print(f"入力ファイル: {file_path}")
    print(f"出力ディレクトリ: {output_dir}")
    
    # 1. データ読み込み
    print("\n[1/6] データを読み込んでいます...")
    loader = DataLoader()
    df = loader.load_file(file_path)
    print(f"  読み込み完了: {len(df):,} 行")
    
    # 2. データ前処理
    print("\n[2/6] データを前処理しています...")
    processor = DataProcessor()
    df = processor.clean_data(df)
    df = processor.remove_invalid_rows(df)
    print(f"  有効データ: {len(df):,} 行")
    
    # 3. Uplift計算
    print("\n[3/6] Upliftを計算しています...")
    calculator = UpliftCalculator()
    df = calculator.add_uplift_column(df)
    print(f"  Uplift計算完了: {len(df):,} 行")
    
    # 3.5 外れ値除外
    print("\n[3.5/6] 外れ値を除外しています...")
    original_count = len(df)
    df = processor.remove_outliers(df, 'uplift', method='percentile', lower_percentile=1, upper_percentile=99)
    removed_count = original_count - len(df)
    print(f"  外れ値除外: {removed_count:,} 行を除外 ({removed_count/original_count*100:.1f}%)")
    print(f"  分析対象: {len(df):,} 行")
    
    # 4. 統計分析
    print("\n[4/6] 統計分析を実行しています...")
    analyzer = StatisticalAnalyzer()
    regression_result = analyzer.run_regression(df)
    interpretation = analyzer.interpret_results(regression_result)
    descriptive_stats = analyzer.calculate_descriptive_stats(df)
    print("  回帰分析完了")
    
    # 5. 視覚化
    print("\n[5/6] グラフを生成しています...")
    visualizer = Visualizer()
    
    figures = []
    
    # 散布図: 価格 vs Uplift
    fig1 = visualizer.create_scatter_plot(
        df, 'our_price', 'uplift',
        title='価格とUpliftの関係',
        x_label='価格 (our_price)',
        y_label='Uplift (%)'
    )
    figures.append((fig1, f'uplift_price_scatter_{timestamp}.png'))
    
    # 散布図: 割引率 vs Uplift
    fig2 = visualizer.create_scatter_plot(
        df, 'discount_percent_numeric', 'uplift',
        title='割引率とUpliftの関係',
        x_label='割引率 (%)',
        y_label='Uplift (%)'
    )
    figures.append((fig2, f'uplift_discount_scatter_{timestamp}.png'))
    
    # ヒートマップ
    fig3 = visualizer.create_heatmap(
        df, 'our_price', 'discount_percent_numeric', 'uplift',
        title='価格×割引率のUplift平均',
        x_label='価格帯',
        y_label='割引率帯'
    )
    figures.append((fig3, f'uplift_heatmap_{timestamp}.png'))
    
    # 交互作用プロット
    fig4 = visualizer.create_interaction_plot(df)
    figures.append((fig4, f'uplift_interaction_{timestamp}.png'))
    
    # グラフを保存
    figure_paths = visualizer.save_figures(figures, output_dir)
    print(f"  {len(figure_paths)} 個のグラフを保存しました")

    
    # 6. 結果をまとめる
    print("\n[6/6] レポートを生成しています...")
    result = AnalysisResult(
        regression=regression_result,
        interpretation=interpretation,
        descriptive_stats=descriptive_stats,
        figure_paths=figure_paths
    )
    
    # レポート出力
    reporter = ReportGenerator()
    reporter.print_summary(result)
    
    # JSON出力
    json_path = str(Path(output_dir) / f'uplift_analysis_{timestamp}.json')
    reporter.export_json(result, json_path)
    
    # HTMLレポート出力
    html_reporter = HTMLReportGenerator()
    html_path = str(Path(output_dir) / f'uplift_analysis_{timestamp}.html')
    html_reporter.generate_report(result, html_path)
    print(f"HTMLレポートを保存しました: {html_path}")
    
    return result


def main():
    """メイン関数"""
    if len(sys.argv) < 2:
        print("使用方法: python run_uplift_analysis.py <ファイルパス> [出力ディレクトリ]")
        print("\n例:")
        print('  python run_uplift_analysis.py "C:\\data\\BF25_OPSByASIN.txt"')
        print('  python run_uplift_analysis.py "C:\\data\\BF25_OPSByASIN.txt" "C:\\output"')
        sys.exit(1)
    
    file_path = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else None
    
    try:
        result = run_analysis(file_path, output_dir)
        print("\n分析が完了しました。")
    except FileNotFoundError as e:
        print(f"\nエラー: {e}")
        sys.exit(1)
    except MissingColumnError as e:
        print(f"\nエラー: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n予期しないエラーが発生しました: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
