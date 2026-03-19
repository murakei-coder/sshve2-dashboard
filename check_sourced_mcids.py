"""
Check MCIDs with SSHVE2_SourcedFlag=Y to verify data
"""
import pandas as pd

sourcing_file = r'C:\Users\murakei\Desktop\SSHVE2\Sourcing\Tracking\Sourcing_data_raw_Sourcing更新.csv'
df = pd.read_csv(sourcing_file, encoding='utf-8-sig', low_memory=False)

# Get MCIDs with Y flag
y_data = df[df['SSHVE2_SourcedFlag'] == 'Y']
print(f"Total rows with SSHVE2_SourcedFlag=Y: {len(y_data)}")

# Group by MCID and sum GMS
mcid_gms = y_data.groupby('mcid')['total_t30d_gms_BAU'].sum().sort_values(ascending=False)
print(f"\nTop 10 MCIDs by Sourced GMS:")
for mcid, gms in mcid_gms.head(10).items():
    print(f"  {mcid}: {gms:,.0f}")

# Check a specific MCID with Y flag
sample_mcid = mcid_gms.index[0]
sample_data = df[df['mcid'] == sample_mcid]
print(f"\nSample MCID {sample_mcid}:")
print(f"  Total ASINs: {len(sample_data)}")
print(f"  SSHVE2_SourcedFlag=Y: {len(sample_data[sample_data['SSHVE2_SourcedFlag']=='Y'])}")
print(f"  SSHVE2_SourcedFlag=N: {len(sample_data[sample_data['SSHVE2_SourcedFlag']=='N'])}")
print(f"  Sourced GMS: {sample_data[sample_data['SSHVE2_SourcedFlag']=='Y']['total_t30d_gms_BAU'].sum():,.0f}")
