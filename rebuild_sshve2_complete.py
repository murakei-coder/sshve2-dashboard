"""
Rebuild Complete SSHVE2 Dashboard Data
Combines data from multiple sources:
1. Merchant names from Excel
2. Sourcing data from CSV (with SSHVE2_SourcedFlag filtering)
3. Existing aggregated data
"""
import pandas as pd
import json
from datetime import datetime

print("=" * 80)
print("Rebuilding Complete SSHVE2 Dashboard Data")
print("=" * 80)

# Load merchant names
merchant_file = r'C:\Users\murakei\Desktop\SSHVE2\Dashboard\raw\CID ASIN SSHVE2_ALL PF.xlsx'
print(f"\n1. Loading merchant names: {merchant_file}")
df_merchant = pd.read_excel(merchant_file)
print(f"   ✅ Loaded {len(df_merchant)} rows")

# Create merchant name lookup
merchant_lookup = {}
for _, row in df_merchant.iterrows():
    mcid = str(row['mcid'])
    merchant_lookup[mcid] = {
        'merchant_name': row['merchant name'],
        'team': row['Team'],
        'alias': row['Alias'],
        'mgr': row['Mgr'] if pd.notna(row['Mgr']) else None
    }
print(f"   ✅ Created lookup for {len(merchant_lookup)} MCIDs")

# Load sourcing data
sourcing_file = r'C:\Users\murakei\Desktop\SSHVE2\Sourcing\Tracking\Sourcing_data_raw_Sourcing更新.csv'
print(f"\n2. Loading sourcing data: {sourcing_file}")
df_sourcing = pd.read_csv(sourcing_file, encoding='utf-8-sig')
print(f"   ✅ Loaded {len(df_sourcing)} rows")
print(f"   ✅ Columns: {list(df_sourcing.columns)[:10]}...")  # Show first 10 columns

# Check for sample MCID
sample_mcid = '48354301822'
sample_sourcing = df_sourcing[df_sourcing['mcid'].astype(str) == sample_mcid]
if not sample_sourcing.empty:
    print(f"\n   Sample MCID {sample_mcid}:")
    print(f"     Total rows: {len(sample_sourcing)}")
    if 'SSHVE2_SourcedFlag' in df_sourcing.columns:
        sourced_count = len(sample_sourcing[sample_sourcing['SSHVE2_SourcedFlag'] == 'Y'])
        not_sourced_count = len(sample_sourcing[sample_sourcing['SSHVE2_SourcedFlag'] == 'N'])
        print(f"     SSHVE2_SourcedFlag=Y: {sourced_count}")
        print(f"     SSHVE2_SourcedFlag=N: {not_sourced_count}")
        if 'T30 GMS' in df_sourcing.columns:
            sourced_gms = sample_sourcing[sample_sourcing['SSHVE2_SourcedFlag'] == 'Y']['T30 GMS'].sum()
            print(f"     Sourced GMS (Y only): {sourced_gms:,.0f}")

# Load existing JSON data for suppression rates and targets
existing_json = 'sshve2_data_v2_20260318_203513.json'
print(f"\n3. Loading existing data: {existing_json}")
with open(existing_json, 'r', encoding='utf-8') as f:
    existing_data = json.load(f)
print(f"   ✅ Loaded {len(existing_data['cids'])} MCIDs")

# Create lookup for existing data
existing_lookup = {c['cid']: c for c in existing_data['cids']}

# Define coefficients
coefficients = existing_data.get('coefficients', {
    'No suppression': 0.5343,
    'OOS': 0.2807,
    'VRP Missing': 0.0963,
    'Price Error': 0.275,
    'Others': 0.1801
})

print(f"\n4. Processing and merging data...")
cid_data = []
cids_processed = 0

# Group sourcing data by MCID
for mcid, group in df_sourcing.groupby('mcid'):
    mcid_str = str(mcid)
    cids_processed += 1
    if cids_processed % 500 == 0:
        print(f"   Processed {cids_processed} MCIDs...")
    
    # Get merchant info
    merchant_info = merchant_lookup.get(mcid_str, {})
    merchant_name = merchant_info.get('merchant_name')
    team = merchant_info.get('team')
    alias = merchant_info.get('alias')
    mgr = merchant_info.get('mgr')
    
    # Get existing data for suppression rates and targets
    existing = existing_lookup.get(mcid_str, {})
    
    # Calculate Sourced GMS: Only SSHVE2_SourcedFlag = Y
    if 'SSHVE2_SourcedFlag' in group.columns and 'total_t30d_gms_BAU' in group.columns:
        sourced_rows = group[group['SSHVE2_SourcedFlag'] == 'Y']
        current_gms = sourced_rows['total_t30d_gms_BAU'].sum()
    else:
        # If no sourcing data, set to 0 (don't use existing data which may be incorrect)
        current_gms = 0
    
    # Target GMS from existing data
    target_gms = existing.get('target_gms', 0)
    gap = current_gms - target_gms
    
    # Past participation: SSHVE2_SourcedFlag = N AND 対象 = Y
    if 'SSHVE2_SourcedFlag' in group.columns and '対象' in group.columns and 'total_t30d_gms_BAU' in group.columns:
        past_rows = group[(group['SSHVE2_SourcedFlag'] == 'N') & (group['対象'] == 'Y')]
        past_asin_count = len(past_rows)
        past_t30_gms = past_rows['total_t30d_gms_BAU'].sum()
    else:
        past_asin_count = 0
        past_t30_gms = 0
    
    # Event participation from existing data
    event_participation = existing.get('event_participation', {
        'sshve1_flag': {'asin_count': 0},
        't365_flag': {'asin_count': 0}
    })
    
    # Add past participation data
    event_participation['past_participation'] = {
        'asin_count': past_asin_count,
        't30_gms': float(past_t30_gms)
    }
    
    # Suppression rates from existing data
    sshve1_suppression = existing.get('sshve1_suppression', {
        'No suppression': 0, 'OOS': 0, 'VRP Missing': 0, 'Price Error': 0, 'Others': 0
    })
    sshve2_suppression = existing.get('sshve2_suppression', {
        'No suppression': 0, 'OOS': 0, 'VRP Missing': 0, 'Price Error': 0, 'Others': 0
    })
    
    # Calculate Target OPS: Σ(Target GMS × SSHVE1% × coefficient)
    target_ops = sum(target_gms * sshve1_suppression[cat] / 100 * coefficients[cat] 
                     for cat in coefficients.keys())
    
    # Calculate Forecast OPS: Σ(Current GMS × SSHVE2% × coefficient)
    forecast_ops = sum(current_gms * sshve2_suppression[cat] / 100 * coefficients[cat] 
                       for cat in coefficients.keys())
    
    # vs Target OPS
    vs_target_ops = forecast_ops - target_ops
    
    cid_data.append({
        'cid': mcid_str,
        'merchant_name': merchant_name,
        'alias': alias,
        'mgr': mgr,
        'team': team,
        'current_gms': float(current_gms),
        'target_gms': float(target_gms),
        'gap': float(gap),
        'event_participation': event_participation,
        'sshve1_suppression': sshve1_suppression,
        'sshve2_suppression': sshve2_suppression,
        'forecast_ops': float(forecast_ops),
        'target_ops': float(target_ops),
        'vs_target_ops': float(vs_target_ops)
    })

print(f"   ✅ Processed {len(cid_data)} MCIDs")

# Save to JSON
output_json = {
    'cids': cid_data,
    'coefficients': coefficients,
    'metadata': {
        'generated_at': datetime.now().isoformat(),
        'merchant_file': merchant_file,
        'sourcing_file': sourcing_file,
        'existing_file': existing_json,
        'total_cids': len(cid_data)
    }
}

output_file = f'sshve2_data_complete_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(output_json, f, ensure_ascii=False, indent=2)

print(f"\n✅ Saved to: {output_file}")

# Verify sample MCID
if sample_mcid in [c['cid'] for c in cid_data]:
    sample_cid_data = next(c for c in cid_data if c['cid'] == sample_mcid)
    print(f"\n" + "=" * 80)
    print(f"Verification - MCID {sample_mcid}:")
    print(f"  Merchant Name: {sample_cid_data['merchant_name']}")
    print(f"  Team: {sample_cid_data['team']}")
    print(f"  Alias: {sample_cid_data['alias']}")
    print(f"  Mgr: {sample_cid_data['mgr']}")
    print(f"  Sourced GMS (Act): {sample_cid_data['current_gms']:,.0f}")
    print(f"  Target GMS: {sample_cid_data['target_gms']:,.0f}")
    print(f"  Past Participation ASINs: {sample_cid_data['event_participation']['past_participation']['asin_count']}")
    print(f"  Past Participation T30 GMS: {sample_cid_data['event_participation']['past_participation']['t30_gms']:,.0f}")
    print(f"  Forecast OPS: {sample_cid_data['forecast_ops']:,.0f}")
    print(f"  Target OPS: {sample_cid_data['target_ops']:,.0f}")
    print("=" * 80)

print("\n✨ Data rebuild complete!")
print("=" * 80)
