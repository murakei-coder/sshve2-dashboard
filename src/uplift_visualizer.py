"""
Uplift Interaction Analyzer - Visualizer

視覚化機能
- 散布図（price vs uplift, discount vs uplift）
- ヒートマップ（price × discount のUplift平均）
- PNG保存機能
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # GUIなしで動作させる
import seaborn as sns
from typing import List, Tuple, Optional
from pathlib import Path


class Visualizer:
    """グラフを生成するクラス"""
    
    def __init__(self, figsize: Tuple[int, int] = (10, 8)):
        """
        Args:
            figsize: 図のサイズ（幅, 高さ）
        """
        self.figsize = figsize
        # 日本語フォント設定
        plt.rcParams['font.family'] = ['MS Gothic', 'Hiragino Sans', 'sans-serif']
        plt.rcParams['axes.unicode_minus'] = False
    
    def create_scatter_plot(
        self, 
        df: pd.DataFrame, 
        x_col: str, 
        y_col: str,
        title: str,
        x_label: str,
        y_label: str
    ) -> plt.Figure:
        """
        散布図を生成
        
        Args:
            df: データ
            x_col: X軸のカラム名
            y_col: Y軸のカラム名
            title: グラフタイトル
            x_label: X軸ラベル
            y_label: Y軸ラベル
            
        Returns:
            Figure: matplotlib Figure
        """
        fig, ax = plt.subplots(figsize=self.figsize)
        
        ax.scatter(df[x_col], df[y_col], alpha=0.5, s=10)
        ax.set_xlabel(x_label)
        ax.set_ylabel(y_label)
        ax.set_title(title)
        
        # 回帰直線を追加
        z = np.polyfit(df[x_col], df[y_col], 1)
        p = np.poly1d(z)
        x_line = np.linspace(df[x_col].min(), df[x_col].max(), 100)
        ax.plot(x_line, p(x_line), "r--", alpha=0.8, label=f'回帰直線')
        ax.legend()
        
        plt.tight_layout()
        return fig
    
    def create_heatmap(
        self,
        df: pd.DataFrame,
        x_col: str,
        y_col: str,
        value_col: str,
        title: str,
        x_label: str,
        y_label: str,
        n_bins: int = 10
    ) -> plt.Figure:
        """
        ヒートマップを生成
        
        Args:
            df: データ
            x_col: X軸のカラム名（ビニング対象）
            y_col: Y軸のカラム名（ビニング対象）
            value_col: 値のカラム名
            title: グラフタイトル
            x_label: X軸ラベル
            y_label: Y軸ラベル
            n_bins: ビンの数
            
        Returns:
            Figure: matplotlib Figure
        """
        df = df.copy()
        
        # ビニング
        df['x_bin'] = pd.cut(df[x_col], bins=n_bins)
        df['y_bin'] = pd.cut(df[y_col], bins=n_bins)
        
        # ピボットテーブルを作成
        pivot = df.pivot_table(
            values=value_col,
            index='y_bin',
            columns='x_bin',
            aggfunc='mean'
        )
        
        fig, ax = plt.subplots(figsize=(12, 10))
        
        sns.heatmap(
            pivot,
            annot=True,
            fmt='.1f',
            cmap='RdYlGn',
            center=0,
            ax=ax,
            cbar_kws={'label': f'平均 {value_col}'}
        )
        
        ax.set_xlabel(x_label)
        ax.set_ylabel(y_label)
        ax.set_title(title)
        
        # X軸ラベルを回転
        plt.xticks(rotation=45, ha='right')
        plt.yticks(rotation=0)
        
        plt.tight_layout()
        return fig

    
    def create_interaction_plot(
        self,
        df: pd.DataFrame,
        title: str = "価格×割引率の交互作用効果"
    ) -> plt.Figure:
        """
        交互作用効果を視覚化するプロット
        
        価格帯ごとに割引率とUpliftの関係を表示
        
        Args:
            df: データ
            title: グラフタイトル
            
        Returns:
            Figure: matplotlib Figure
        """
        df = df.copy()
        
        # 価格を4分位でグループ化
        df['price_group'] = pd.qcut(
            df['our_price'], 
            q=4, 
            labels=['低価格', '中低価格', '中高価格', '高価格']
        )
        
        fig, ax = plt.subplots(figsize=self.figsize)
        
        colors = ['blue', 'green', 'orange', 'red']
        
        for i, (name, group) in enumerate(df.groupby('price_group', observed=True)):
            # 割引率でソートして平均を計算
            group_sorted = group.sort_values('discount_percent_numeric')
            
            # 移動平均を計算
            window = max(len(group_sorted) // 20, 10)
            rolling_mean = group_sorted['uplift'].rolling(window=window, center=True).mean()
            
            ax.scatter(
                group_sorted['discount_percent_numeric'], 
                group_sorted['uplift'],
                alpha=0.3,
                s=5,
                color=colors[i],
                label=f'{name}'
            )
            
            # トレンドラインを追加
            valid_idx = rolling_mean.notna()
            if valid_idx.sum() > 0:
                ax.plot(
                    group_sorted.loc[valid_idx, 'discount_percent_numeric'],
                    rolling_mean[valid_idx],
                    color=colors[i],
                    linewidth=2,
                    linestyle='-'
                )
        
        ax.set_xlabel('割引率 (%)')
        ax.set_ylabel('Uplift (%)')
        ax.set_title(title)
        ax.legend(title='価格帯')
        
        plt.tight_layout()
        return fig
    
    def save_figures(
        self, 
        figures: List[Tuple[plt.Figure, str]], 
        output_dir: str
    ) -> List[str]:
        """
        グラフをPNGとして保存
        
        Args:
            figures: (Figure, ファイル名)のリスト
            output_dir: 出力ディレクトリ
            
        Returns:
            List[str]: 保存したファイルパスのリスト
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        saved_paths = []
        
        for fig, filename in figures:
            file_path = output_path / filename
            fig.savefig(file_path, dpi=150, bbox_inches='tight')
            plt.close(fig)
            saved_paths.append(str(file_path))
        
        return saved_paths
    
    def bin_data(
        self,
        df: pd.DataFrame,
        col: str,
        n_bins: int = 10
    ) -> pd.DataFrame:
        """
        データをビニングする
        
        Args:
            df: データ
            col: ビニング対象のカラム名
            n_bins: ビンの数
            
        Returns:
            pd.DataFrame: ビニング後のデータ
        """
        df = df.copy()
        df[f'{col}_bin'] = pd.cut(df[col], bins=n_bins)
        return df
