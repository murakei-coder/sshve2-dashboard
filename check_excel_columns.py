"""
Check Excel file columns and sample data
"""
import pandas as pd

raw_file = r'C:\Users\murakei\Desktop\SSHVE2\Dashboard\raw\CID ASIN SSHVE2_ALL PF.xlsx'
print(f"Loading: {raw_file}\n")

df = pd.read_excel(raw_file)
print(f"Total rows: {len(df)}")
print(f"\nAll columns ({len(df.columns)}):")
for i, col in enumerate(df.columns, 1):
    print(f"  {i}. '{col}'")

print(f"\n{'='*80}")
print("First 3 rows:")
print(df.head(3).to_string())

print(f"\n{'='*80}")
print("Sample MCID 48354301822:")
sample = df[df['mcid'].astype(str) == '48354301822']
if not sample.empty:
    print(f"  Found {len(sample)} rows")
    print(sample.to_string())
else:
    print("  Not found")
