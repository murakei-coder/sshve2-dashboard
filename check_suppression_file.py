"""
Check new Suppression data file structure
"""
import pandas as pd

suppression_file = r'C:\Users\murakei\Desktop\SSHVE2\Dashboard\raw\Suppression\SSHVE2_ByASIN_Suppression_raw_Final.txt'
print(f"Loading: {suppression_file}\n")

# Try reading as tab-separated
df = pd.read_csv(suppression_file, sep='\t', encoding='utf-8')
print(f"Total rows: {len(df)}")
print(f"\nAll columns ({len(df.columns)}):")
for i, col in enumerate(df.columns, 1):
    print(f"  {i}. '{col}'")

print(f"\n{'='*80}")
print("First 3 rows:")
print(df.head(3))

print(f"\n{'='*80}")
print("Sample data for a specific MCID:")
if 'mcid' in df.columns or 'MCID' in df.columns:
    mcid_col = 'mcid' if 'mcid' in df.columns else 'MCID'
    sample_mcid = df[mcid_col].iloc[0]
    sample = df[df[mcid_col] == sample_mcid]
    print(f"  MCID: {sample_mcid}")
    print(f"  Rows: {len(sample)}")
    print(sample.head(2))

# Check for suppression-related columns
print(f"\n{'='*80}")
print("Suppression-related columns:")
supp_cols = [col for col in df.columns if 'supp' in col.lower() or 'oos' in col.lower() or 'vrp' in col.lower() or 'price' in col.lower()]
print(f"  Found {len(supp_cols)} columns:")
for col in supp_cols:
    print(f"    - {col}")
