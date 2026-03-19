"""
Uplift Interaction Analyzer - Data Models

データモデルクラスの定義
- RegressionCoefficient: 回帰係数
- RegressionResult: 回帰分析結果
- AnalysisInterpretation: 分析結果の解釈
- AnalysisResult: 総合分析結果
"""

from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any, Optional
import json


@dataclass
class RegressionCoefficient:
    """回帰係数を表すデータクラス"""
    name: str           # 変数名（our_price, discount_percent, interaction）
    coefficient: float  # 係数
    std_error: float    # 標準誤差
    t_value: float      # t値
    p_value: float      # p値
    is_significant: bool = field(default=False)  # p < 0.05
    
    def __post_init__(self):
        self.is_significant = bool(self.p_value < 0.05)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'name': self.name,
            'coefficient': float(self.coefficient),
            'std_error': float(self.std_error),
            't_value': float(self.t_value),
            'p_value': float(self.p_value),
            'is_significant': bool(self.is_significant)
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'RegressionCoefficient':
        return cls(**data)


@dataclass
class RegressionResult:
    """回帰分析結果を表すデータクラス"""
    coefficients: List[RegressionCoefficient]
    r_squared: float           # R²
    adj_r_squared: float       # 調整済みR²
    f_statistic: float         # F統計量
    f_p_value: float           # F検定のp値
    n_observations: int        # 観測数
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'coefficients': [c.to_dict() for c in self.coefficients],
            'r_squared': float(self.r_squared),
            'adj_r_squared': float(self.adj_r_squared),
            'f_statistic': float(self.f_statistic),
            'f_p_value': float(self.f_p_value),
            'n_observations': int(self.n_observations)
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'RegressionResult':
        coefficients = [RegressionCoefficient.from_dict(c) for c in data['coefficients']]
        return cls(
            coefficients=coefficients,
            r_squared=data['r_squared'],
            adj_r_squared=data['adj_r_squared'],
            f_statistic=data['f_statistic'],
            f_p_value=data['f_p_value'],
            n_observations=data['n_observations']
        )



@dataclass
class AnalysisInterpretation:
    """分析結果の解釈を表すデータクラス"""
    price_effect: str          # 価格の効果の解釈
    discount_effect: str       # 割引率の効果の解釈
    interaction_effect: str    # 交互作用効果の解釈
    hypothesis_supported: bool # 仮説が支持されたか
    conclusion: str            # 総合的な結論
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'price_effect': self.price_effect,
            'discount_effect': self.discount_effect,
            'interaction_effect': self.interaction_effect,
            'hypothesis_supported': bool(self.hypothesis_supported),
            'conclusion': self.conclusion
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AnalysisInterpretation':
        return cls(**data)


@dataclass
class DescriptiveStats:
    """記述統計を表すデータクラス"""
    variable: str
    count: int
    mean: float
    std: float
    min_val: float
    max_val: float
    median: float
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'variable': self.variable,
            'count': int(self.count),
            'mean': float(self.mean),
            'std': float(self.std),
            'min_val': float(self.min_val),
            'max_val': float(self.max_val),
            'median': float(self.median)
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DescriptiveStats':
        return cls(**data)


@dataclass
class AnalysisResult:
    """総合分析結果を表すデータクラス"""
    regression: RegressionResult
    interpretation: AnalysisInterpretation
    descriptive_stats: List[DescriptiveStats]
    figure_paths: List[str]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'regression': self.regression.to_dict(),
            'interpretation': self.interpretation.to_dict(),
            'descriptive_stats': [s.to_dict() for s in self.descriptive_stats],
            'figure_paths': self.figure_paths
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AnalysisResult':
        return cls(
            regression=RegressionResult.from_dict(data['regression']),
            interpretation=AnalysisInterpretation.from_dict(data['interpretation']),
            descriptive_stats=[DescriptiveStats.from_dict(s) for s in data['descriptive_stats']],
            figure_paths=data['figure_paths']
        )
    
    def to_json(self) -> str:
        """JSON文字列に変換"""
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2)
    
    @classmethod
    def from_json(cls, json_str: str) -> 'AnalysisResult':
        """JSON文字列から復元"""
        data = json.loads(json_str)
        return cls.from_dict(data)
    
    def save_json(self, file_path: str) -> None:
        """JSONファイルに保存"""
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(self.to_json())
    
    @classmethod
    def load_json(cls, file_path: str) -> 'AnalysisResult':
        """JSONファイルから読み込み"""
        with open(file_path, 'r', encoding='utf-8') as f:
            return cls.from_json(f.read())
