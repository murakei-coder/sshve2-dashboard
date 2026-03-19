"""
Rebuild SSHVE2 Data from Raw Excel File
Correctly processes:
- Merchant names from raw file
- Sourced GMS (only SSHVE2_SourcedFlag = Y)
- Past participation ASINs (SSHVE2_SourcedFlag = N, 対象 = Y)
- T30 GMS for past participation
"""
import pandas as pd
import json
from datetime import datetime

print("=" * 80)
print("Rebuilding SSHVE2 Data from Raw Excel File")
print("=" * 80)

# Load raw data
raw_file = r'C:\Users\murakei\Desktop\SSHVE2\Dashboard\raw\CID ASIN SSHVE2_ALL PF.xlsx'
print(f"\nLoading: {raw_file}")

try:
    df = pd.read_excel(raw_file)
    print(f"✅ Loaded {len(df)} rows")
    print(f"✅ Columns: {list(df.columns)}")
except Exception as e:
    print(f"❌ Error loading file: {e}")
    exit(1)

# Display sample data for verification
print("\n" + "=" * 80)
print("Sample Data (first 5 rows):")
print(df.head())
print("\n" + "=" * 80)

# Check for MCID 48354301822
sample_mcid = '48354301822'
sample_data = df[df['mcid'].astype(str) == sample_mcid]
if not sample_data.empty:
    print(f"\nSample MCID {sample_mcid}:")
    print(f"  Total rows: {len(sample_data)}")
    print(f"  SSHVE2_SourcedFlag=Y: {len(sample_data[sample_data['SSHVE2_SourcedFlag']=='Y'])}")
    print(f"  SSHVE2_SourcedFlag=N: {len(sample_data[sample_data['SSHVE2_SourcedFlag']=='N'])}")
    if 'T30 GMS' in df.columns:
        sourced_gms = sample_data[sample_data['SSHVE2_SourcedFlag']=='Y']['T30 GMS'].sum()
        print(f"  Sourced GMS (Y only): {sourced_gms:,.0f}")
    print("\n" + "=" * 80)

# Group by mcid and process
print("\nProcessing data by mcid...")

# Define coefficients
coefficients = {
    'No suppression': 0.5343,
    'OOS': 0.2807,
    'VRP Missing': 0.0963,
    'Price Error': 0.275,
    'Others': 0.1801
}

cid_data = []
cids_processed = 0

for cid, group in df.groupby('mcid'):
    cids_processed += 1
    if cids_processed % 500 == 0:
        print(f"  Processed {cids_processed} CIDs...")
    
    # Get merchant name (first non-null value)
    merchant_name = group['merchant name'].dropna().iloc[0] if 'merchant name' in group.columns and not group['merchant name'].dropna().empty else None
    
    # Get hierarchy info
    alias = group['Alias'].dropna().iloc[0] if 'Alias' in group.columns and not group['Alias'].dropna().empty else None
    mgr = group['Mgr'].dropna().iloc[0] if 'Mgr' in group.columns and not group['Mgr'].dropna().empty else None
    team = group['Team'].dropna().iloc[0] if 'Team' in group.columns and not group['Team'].dropna().empty else None
    
    # Sourced GMS: Only SSHVE2_SourcedFlag = Y
    sourced_rows = group[group['SSHVE2_SourcedFlag'] == 'Y']
    current_gms = sourced_rows['T30 GMS'].sum() if 'T30 GMS' in group.columns else 0
    
    # Target GMS (if available)
    target_gms = group['Target GMS'].dropna().iloc[0] if 'Target GMS' in group.columns and not group['Target GMS'].dropna().empty else 0
    
    # Gap
    gap = current_gms - target_gms
    
    # Past participation ASINs: SSHVE2_SourcedFlag = N AND 対象 = Y
    past_participation_rows = group[(group['SSHVE2_SourcedFlag'] == 'N') & (group['対象'] == 'Y')]
    
    # SSHVE1 participation
    sshve1_asins = len(group[group['SSHVE1_Flag'] == 'Y']) if 'SSHVE1_Flag' in group.columns else 0
    
    # T365 participation  
    t365_asins = len(group[group['T365_Flag'] == 'Y']) if 'T365_Flag' in group.columns else 0
    
    # SSHVE1 Suppression (from first row, should be same for all rows in CID)
    sshve1_suppression = {
        'No suppression': float(group['SSHVE1_No suppression'].iloc[0]) if 'SSHVE1_No suppression' in group.columns else 0,
        'OOS': float(group['SSHVE1_OOS'].iloc[0]) if 'SSHVE1_OOS' in group.columns else 0,
        'VRP Missing': float(group['SSHVE1_VRP Missing'].iloc[0]) if 'SSHVE1_VRP Missing' in group.columns else 0,
        'Price Error': float(group['SSHVE1_Price Error'].iloc[0]) if 'SSHVE1_Price Error' in group.columns else 0,
        'Others': float(group['SSHVE1_Others'].iloc[0]) if 'SSHVE1_Others' in group.columns else 0
    }
    
    # SSHVE2 Suppression (from first row)
    sshve2_suppression = {
        'No suppression': float(group['SSHVE2_No suppression'].iloc[0]) if 'SSHVE2_No suppression' in group.columns else 0,
        'OOS': float(group['SSHVE2_OOS'].iloc[0]) if 'SSHVE2_OOS' in group.columns else 0,
        'VRP Missing': float(group['SSHVE2_VRP Missing'].iloc[0]) if 'SSHVE2_VRP Missing' in group.columns else 0,
        'Price Error': float(group['SSHVE2_Price Error'].iloc[0]) if 'SSHVE2_Price Error' in group.columns else 0,
        'Others': float(group['SSHVE2_Others'].iloc[0]) if 'SSHVE2_Others' in group.columns else 0
    }
    
    # Calculate Target OPS: Σ(Target GMS × SSHVE1% × coefficient)
    target_ops = sum(target_gms * sshve1_suppression[cat] / 100 * coefficients[cat] 
                     for cat in coefficients.keys())
    
    # Calculate Forecast OPS: Σ(Current GMS × SSHVE2% × coefficient)
    forecast_ops = sum(current_gms * sshve2_suppression[cat] / 100 * coefficients[cat] 
                       for cat in coefficients.keys())
    
    # vs Target OPS
    vs_target_ops = forecast_ops - target_ops
    
    cid_data.append({
        'cid': str(cid),
        'merchant_name': merchant_name,
        'alias': alias,
        'mgr': mgr,
        'team': team,
        'current_gms': float(current_gms),
        'target_gms': float(target_gms),
        'gap': float(gap),
        'event_participation': {
            'sshve1_flag': {'asin_count': int(sshve1_asins)},
            't365_flag': {'asin_count': int(t365_asins)},
            'past_participation': {
                'asin_count': len(past_participation_rows),
                't30_gms': float(past_participation_rows['T30 GMS'].sum()) if 'T30 GMS' in group.columns else 0
            }
        },
        'sshve1_suppression': sshve1_suppression,
        'sshve2_suppression': sshve2_suppression,
        'forecast_ops': float(forecast_ops),
        'target_ops': float(target_ops),
        'vs_target_ops': float(vs_target_ops)
    })

print(f"✅ Processed {len(cid_data)} CIDs")

# Save to JSON
output_json = {
    'cids': cid_data,
    'coefficients': coefficients,
    'metadata': {
        'generated_at': datetime.now().isoformat(),
        'source_file': raw_file,
        'total_cids': len(cid_data)
    }
}

output_file = f'sshve2_data_corrected_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(output_json, f, ensure_ascii=False, indent=2)

print(f"\n✅ Saved to: {output_file}")

# Verify sample MCID
if sample_mcid in [c['cid'] for c in cid_data]:
    sample_cid_data = next(c for c in cid_data if c['cid'] == sample_mcid)
    print(f"\n" + "=" * 80)
    print(f"Verification - MCID {sample_mcid}:")
    print(f"  Merchant Name: {sample_cid_data['merchant_name']}")
    print(f"  Sourced GMS: {sample_cid_data['current_gms']:,.0f}")
    print(f"  Target GMS: {sample_cid_data['target_gms']:,.0f}")
    print(f"  Past Participation ASINs: {sample_cid_data['event_participation']['past_participation']['asin_count']}")
    print(f"  Past Participation T30 GMS: {sample_cid_data['event_participation']['past_participation']['t30_gms']:,.0f}")
    print("=" * 80)

print("\n✨ Data rebuild complete!")
print("=" * 80)
