"""
Debug Sourcing CSV to understand column names and data structure
"""
import pandas as pd

sourcing_file = r'C:\Users\murakei\Desktop\SSHVE2\Sourcing\Tracking\Sourcing_data_raw_Sourcing更新.csv'
print(f"Loading: {sourcing_file}\n")

df = pd.read_csv(sourcing_file, encoding='utf-8-sig', low_memory=False)
print(f"Total rows: {len(df)}")
print(f"\nAll columns ({len(df.columns)}):")
for i, col in enumerate(df.columns, 1):
    print(f"  {i}. '{col}'")

print(f"\n{'='*80}")
print("First 3 rows:")
print(df.head(3))

print(f"\n{'='*80}")
print("Sample MCID 48354301822:")
sample = df[df['mcid'].astype(str) == '48354301822']
if not sample.empty:
    print(f"  Found {len(sample)} rows")
    print(f"\n  Columns with data:")
    for col in df.columns:
        if col in sample.columns and not sample[col].isna().all():
            print(f"    {col}: {sample[col].iloc[0]}")
else:
    print("  Not found")

# Check for T30 GMS column variations
print(f"\n{'='*80}")
print("Looking for GMS-related columns:")
gms_cols = [col for col in df.columns if 'gms' in col.lower() or 'GMS' in col]
print(f"  Found {len(gms_cols)} columns: {gms_cols}")

# Check SSHVE2_SourcedFlag values
print(f"\n{'='*80}")
if 'SSHVE2_SourcedFlag' in df.columns:
    print("SSHVE2_SourcedFlag value counts:")
    print(df['SSHVE2_SourcedFlag'].value_counts())
    
    # Sample with Y flag
    y_sample = df[df['SSHVE2_SourcedFlag'] == 'Y'].head(3)
    if not y_sample.empty:
        print(f"\nSample rows with SSHVE2_SourcedFlag=Y:")
        print(y_sample[['mcid', 'SSHVE2_SourcedFlag'] + gms_cols])
