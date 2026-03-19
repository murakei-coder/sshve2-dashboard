"""
Uplift Interaction Analyzer - Report Generator

レポート生成機能
- コンソールへのサマリー表示
- JSON出力
"""

from typing import Optional
from pathlib import Path

from uplift_models import AnalysisResult, RegressionResult, AnalysisInterpretation


class ReportGenerator:
    """レポートを生成するクラス"""
    
    def print_summary(self, result: AnalysisResult) -> None:
        """
        コンソールにサマリーを表示
        
        Args:
            result: 分析結果
        """
        print("\n" + "=" * 80)
        print("Uplift交互作用分析レポート")
        print("=" * 80)
        
        # 記述統計
        print("\n【記述統計】")
        print("-" * 40)
        for stats in result.descriptive_stats:
            print(f"\n{stats.variable}:")
            print(f"  件数: {stats.count:,}")
            print(f"  平均: {stats.mean:,.2f}")
            print(f"  標準偏差: {stats.std:,.2f}")
            print(f"  最小: {stats.min_val:,.2f}")
            print(f"  最大: {stats.max_val:,.2f}")
            print(f"  中央値: {stats.median:,.2f}")
        
        # 回帰分析結果
        print("\n【回帰分析結果】")
        print("-" * 40)
        reg = result.regression
        print(f"観測数: {reg.n_observations:,}")
        print(f"R²: {reg.r_squared:.4f}")
        print(f"調整済みR²: {reg.adj_r_squared:.4f}")
        print(f"F統計量: {reg.f_statistic:.4f}")
        print(f"F検定 p値: {reg.f_p_value:.4e}")
        
        print("\n【係数】")
        print("-" * 40)
        print(f"{'変数名':<20} {'係数':>15} {'標準誤差':>12} {'t値':>10} {'p値':>12} {'有意性':>8}")
        print("-" * 80)
        for coef in reg.coefficients:
            sig = "***" if coef.p_value < 0.001 else "**" if coef.p_value < 0.01 else "*" if coef.p_value < 0.05 else ""
            print(f"{coef.name:<20} {coef.coefficient:>15.6f} {coef.std_error:>12.6f} {coef.t_value:>10.4f} {coef.p_value:>12.4e} {sig:>8}")
        
        print("\n有意性: *** p<0.001, ** p<0.01, * p<0.05")
        
        # 解釈
        print("\n【分析結果の解釈】")
        print("-" * 40)
        interp = result.interpretation
        print(f"\n価格の効果:\n  {interp.price_effect}")
        print(f"\n割引率の効果:\n  {interp.discount_effect}")
        print(f"\n交互作用効果:\n  {interp.interaction_effect}")
        
        # 結論
        print("\n【結論】")
        print("-" * 40)
        print(f"\n{interp.conclusion}")
        
        if interp.hypothesis_supported:
            print("\n✓ 仮説「価格と割引率が組み合わさるとUpliftへの影響はさらに大きくなる」は支持されました。")
        else:
            print("\n✗ 仮説「価格と割引率が組み合わさるとUpliftへの影響はさらに大きくなる」は支持されませんでした。")
        
        # グラフ
        if result.figure_paths:
            print("\n【生成されたグラフ】")
            print("-" * 40)
            for path in result.figure_paths:
                print(f"  - {path}")
        
        print("\n" + "=" * 80)
    
    def export_json(self, result: AnalysisResult, output_path: str) -> str:
        """
        JSON形式で出力
        
        Args:
            result: 分析結果
            output_path: 出力ファイルパス
            
        Returns:
            str: 保存したファイルパス
        """
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        result.save_json(str(path))
        print(f"\n分析結果をJSONファイルに保存しました: {path}")
        
        return str(path)
