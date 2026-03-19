"""外れ値分析スクリプト"""
import pandas as pd
import numpy as np
import sys
sys.path.insert(0, 'src')
from uplift_data_processor import DataProcessor
from uplift_calculator import UpliftCalculator

df = pd.read_csv(r'C:\Users\murakei\Desktop\BF25_Kiro\BF25_OPSByASIN T30GMSgl.txt', sep='\t')
processor = DataProcessor()
df = processor.clean_data(df)
df = processor.remove_invalid_rows(df)

calculator = UpliftCalculator()
df = calculator.add_uplift_column(df)

print('=== Uplift の分布 ===')
print(df['uplift'].describe())
print()
print('=== 外れ値の確認 ===')
print(f"Uplift > 1000%: {(df['uplift'] > 1000).sum():,} 件")
print(f"Uplift > 10000%: {(df['uplift'] > 10000).sum():,} 件")
print(f"Uplift > 100000%: {(df['uplift'] > 100000).sum():,} 件")
print(f"Uplift < -50%: {(df['uplift'] < -50).sum():,} 件")
print()
print('=== 極端な外れ値のサンプル（上位10件）===')
extreme = df.nlargest(10, 'uplift')[['our_price', 'discount_percent_numeric', 'promotion_ops', 'past_month_gms', 'uplift']]
print(extreme.to_string())
print()
print('=== パーセンタイル分布 ===')
percentiles = [1, 5, 10, 25, 50, 75, 90, 95, 99]
for p in percentiles:
    val = np.percentile(df['uplift'], p)
    print(f"{p}%ile: {val:.2f}")
print()
print('=== 価格帯別のUplift平均 ===')
df['price_bin'] = pd.qcut(df['our_price'], q=5, labels=['Very Low', 'Low', 'Medium', 'High', 'Very High'])
print(df.groupby('price_bin', observed=True)['uplift'].agg(['mean', 'median', 'std', 'count']))
print()
print('=== 割引率帯別のUplift平均 ===')
df['discount_bin'] = pd.cut(df['discount_percent_numeric'], bins=[0, 10, 15, 20, 25, 100], labels=['0-10%', '10-15%', '15-20%', '20-25%', '25%+'])
print(df.groupby('discount_bin', observed=True)['uplift'].agg(['mean', 'median', 'std', 'count']))
