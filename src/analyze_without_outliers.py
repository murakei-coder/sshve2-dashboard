"""外れ値除外後の分析"""
import pandas as pd
import numpy as np
import statsmodels.api as sm
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

print(f"元データ: {len(df):,} 件")

# 外れ値を除外（IQR法）
Q1 = df['uplift'].quantile(0.25)
Q3 = df['uplift'].quantile(0.75)
IQR = Q3 - Q1
lower_bound = Q1 - 1.5 * IQR
upper_bound = Q3 + 1.5 * IQR

print(f"IQR: {IQR:.2f}")
print(f"下限: {lower_bound:.2f}, 上限: {upper_bound:.2f}")

df_clean = df[(df['uplift'] >= lower_bound) & (df['uplift'] <= upper_bound)]
print(f"外れ値除外後: {len(df_clean):,} 件 ({len(df_clean)/len(df)*100:.1f}%)")

print("\n=== 外れ値除外後のUplift分布 ===")
print(df_clean['uplift'].describe())

# 回帰分析（外れ値除外後）
print("\n=== 外れ値除外後の回帰分析 ===")
X = df_clean[['our_price', 'discount_percent_numeric']].copy()
X.columns = ['price', 'discount']
X['interaction'] = X['price'] * X['discount']
X = sm.add_constant(X)
y = df_clean['uplift']

model = sm.OLS(y, X)
results = model.fit()
print(results.summary())

# パーセンタイルで外れ値除外（1-99%）
print("\n\n=== 1-99パーセンタイルで外れ値除外 ===")
p1 = df['uplift'].quantile(0.01)
p99 = df['uplift'].quantile(0.99)
df_p99 = df[(df['uplift'] >= p1) & (df['uplift'] <= p99)]
print(f"1-99%ile除外後: {len(df_p99):,} 件")

X2 = df_p99[['our_price', 'discount_percent_numeric']].copy()
X2.columns = ['price', 'discount']
X2['interaction'] = X2['price'] * X2['discount']
X2 = sm.add_constant(X2)
y2 = df_p99['uplift']

model2 = sm.OLS(y2, X2)
results2 = model2.fit()
print(results2.summary())
