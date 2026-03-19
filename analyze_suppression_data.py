"""
Analyze suppression data structure and categories
"""
import pandas as pd

suppression_file = r'C:\Users\murakei\Desktop\SSHVE2\Dashboard\raw\Suppression\SSHVE2_ByASIN_Suppression_raw_Final.txt'
df = pd.read_csv(suppression_file, sep='\t', encoding='utf-8')

print(f"Total rows: {len(df):,}")
print(f"Unique MCIDs: {df['merchant_customer_id'].nunique():,}")
print(f"Unique ASINs: {df['asin'].nunique():,}")

print(f"\n{'='*80}")
print("Suppression categories (suppression_category_large):")
print(df['suppression_category_large'].value_counts())

print(f"\n{'='*80}")
print("Sample MCID: 851346684")
sample = df[df['merchant_customer_id'] == 851346684]
if not sample.empty:
    print(f"  Total rows: {len(sample)}")
    print(f"  Unique ASINs: {sample['asin'].nunique()}")
    print(f"\n  Suppression breakdown:")
    print(sample['suppression_category_large'].value_counts())
    print(f"\n  Sample rows:")
    print(sample[['merchant_customer_id', 'asin', 'suppression_category_large', 't30d_ops']].head(5))
else:
    print("  Not found")

# Check how to aggregate by MCID
print(f"\n{'='*80}")
print("Aggregation logic test for MCID 851346684:")
if not sample.empty:
    # Group by suppression category and sum OPS
    by_category = sample.groupby('suppression_category_large')['t30d_ops'].sum()
    total_ops = by_category.sum()
    print(f"\n  Total OPS: {total_ops:,.0f}")
    print(f"\n  By category:")
    for cat, ops in by_category.items():
        pct = (ops / total_ops * 100) if total_ops > 0 else 0
        print(f"    {cat}: {ops:,.0f} ({pct:.1f}%)")
