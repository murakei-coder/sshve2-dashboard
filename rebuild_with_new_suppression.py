"""
Rebuild SSHVE2 Data with New Suppression Data
Uses the new suppression file for SSHVE2 suppression rates
"""
import pandas as pd
import json
from datetime import datetime

print("=" * 80)
print("Rebuilding SSHVE2 Data with New Suppression Data")
print("=" * 80)

# Load merchant names
merchant_file = r'C:\Users\murakei\Desktop\SSHVE2\Dashboard\raw\CID ASIN SSHVE2_ALL PF.xlsx'
print(f"\n1. Loading merchant names: {merchant_file}")
df_merchant = pd.read_excel(merchant_file)
merchant_lookup = {str(row['mcid']): {
    'merchant_name': row['merchant name'],
    'team': row['Team'],
    'alias': row['Alias'],
    'mgr': row['Mgr'] if pd.notna(row['Mgr']) else None
} for _, row in df_merchant.iterrows()}
print(f"   ✅ Created lookup for {len(merchant_lookup)} MCIDs")

# Load sourcing data
sourcing_file = r'C:\Users\murakei\Desktop\SSHVE2\Sourcing\Tracking\Sourcing_data_raw_Sourcing更新.csv'
print(f"\n2. Loading sourcing data: {sourcing_file}")
df_sourcing = pd.read_csv(sourcing_file, encoding='utf-8-sig', low_memory=False)
print(f"   ✅ Loaded {len(df_sourcing)} rows")

# Load NEW suppression data
suppression_file = r'C:\Users\murakei\Desktop\SSHVE2\Dashboard\raw\Suppression\SSHVE2_ByASIN_Suppression_raw_Final.txt'
print(f"\n3. Loading NEW suppression data: {suppression_file}")
df_suppression = pd.read_csv(suppression_file, sep='\t', encoding='utf-8')
print(f"   ✅ Loaded {len(df_suppression):,} rows")
print(f"   ✅ Unique MCIDs: {df_suppression['merchant_customer_id'].nunique():,}")

# Map suppression categories (remove numbers)
category_mapping = {
    '1.no suppression': 'No suppression',
    '2.OOS': 'OOS',
    '3.VRP missing': 'VRP Missing',
    '4.Price Error': 'Price Error',
    '5.Others': 'Others'
}

# Calculate SSHVE2 suppression rates by MCID
print(f"\n4. Calculating SSHVE2 suppression rates...")
sshve2_suppression_lookup = {}
for mcid, group in df_suppression.groupby('merchant_customer_id'):
    mcid_str = str(mcid)
    # Sum OPS by category
    by_category = group.groupby('suppression_category_large')['t30d_ops'].sum()
    total_ops = by_category.sum()
    
    # Calculate percentages
    suppression = {
        'No suppression': 0,
        'OOS': 0,
        'VRP Missing': 0,
        'Price Error': 0,
        'Others': 0
    }
    
    if total_ops > 0:
        for cat_raw, ops in by_category.items():
            cat_clean = category_mapping.get(cat_raw, cat_raw)
            if cat_clean in suppression:
                suppression[cat_clean] = (ops / total_ops * 100)
    
    sshve2_suppression_lookup[mcid_str] = suppression

print(f"   ✅ Calculated suppression for {len(sshve2_suppression_lookup)} MCIDs")

# Calculate overall GMS-weighted no suppression rate from raw data
print(f"\n5. Calculating overall GMS-weighted no suppression rate...")
overall_no_supp_ops = df_suppression[df_suppression['suppression_category_large'] == '1.no suppression']['t30d_ops'].sum()
overall_total_ops = df_suppression['t30d_ops'].sum()
overall_no_supp_rate = (overall_no_supp_ops / overall_total_ops * 100) if overall_total_ops > 0 else 0
print(f"   ✅ Overall No Suppression Rate (GMS-weighted): {overall_no_supp_rate:.2f}%")

# Load existing JSON for SSHVE1 and targets
existing_json = 'sshve2_data_v2_20260318_203513.json'
print(f"\n6. Loading existing data for SSHVE1 and targets: {existing_json}")
with open(existing_json, 'r', encoding='utf-8') as f:
    existing_data = json.load(f)
existing_lookup = {c['cid']: c for c in existing_data['cids']}
print(f"   ✅ Loaded {len(existing_data['cids'])} MCIDs")

# Define coefficients
coefficients = existing_data.get('coefficients', {
    'No suppression': 0.5343,
    'OOS': 0.2807,
    'VRP Missing': 0.0963,
    'Price Error': 0.275,
    'Others': 0.1801
})

print(f"\n7. Processing and merging all data...")
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
    
    # Get existing data for SSHVE1 and targets
    existing = existing_lookup.get(mcid_str, {})
    
    # Calculate Sourced GMS: Only SSHVE2_SourcedFlag = Y
    if 'SSHVE2_SourcedFlag' in group.columns and 'total_t30d_gms_BAU' in group.columns:
        sourced_rows = group[group['SSHVE2_SourcedFlag'] == 'Y']
        current_gms = sourced_rows['total_t30d_gms_BAU'].sum()
    else:
        current_gms = 0
    
    # Target GMS from existing data
    target_gms = existing.get('target_gms', 0)
    gap = current_gms - target_gms
    
    # Past participation - Not sourced this time but participated in past events
    # SSHVE1: SSHVE2_SourcedFlag='N' AND sshve1_flag='Y'
    # T365: SSHVE2_SourcedFlag='N' AND t365_flag='Y'
    sshve1_past_gms = 0
    t365_past_gms = 0
    
    if 'SSHVE2_SourcedFlag' in group.columns and 'total_t30d_gms_BAU' in group.columns:
        not_sourced = group[group['SSHVE2_SourcedFlag'] == 'N']
        
        if 'sshve1_flag' in group.columns:
            sshve1_past_rows = not_sourced[not_sourced['sshve1_flag'] == 'Y']
            sshve1_past_gms = sshve1_past_rows['total_t30d_gms_BAU'].sum()
        
        if 't365_flag' in group.columns:
            t365_past_rows = not_sourced[not_sourced['t365_flag'] == 'Y']
            t365_past_gms = t365_past_rows['total_t30d_gms_BAU'].sum()
    
    # Event participation from existing data
    event_participation = existing.get('event_participation', {
        'sshve1_flag': {'asin_count': 0},
        't365_flag': {'asin_count': 0}
    })
    event_participation['past_participation'] = {
        'sshve1_gms': float(sshve1_past_gms),
        't365_gms': float(t365_past_gms)
    }
    
    # SSHVE1 suppression from existing data
    sshve1_suppression = existing.get('sshve1_suppression', {
        'No suppression': 0, 'OOS': 0, 'VRP Missing': 0, 'Price Error': 0, 'Others': 0
    })
    
    # SSHVE2 suppression from NEW data
    sshve2_suppression = sshve2_suppression_lookup.get(mcid_str, {
        'No suppression': 0, 'OOS': 0, 'VRP Missing': 0, 'Price Error': 0, 'Others': 0
    })
    
    # Calculate Target OPS
    target_ops = sum(target_gms * sshve1_suppression[cat] / 100 * coefficients[cat] 
                     for cat in coefficients.keys())
    
    # Calculate Forecast OPS
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
    'overall_no_suppression_rate': overall_no_supp_rate,
    'metadata': {
        'generated_at': datetime.now().isoformat(),
        'merchant_file': merchant_file,
        'sourcing_file': sourcing_file,
        'suppression_file': suppression_file,
        'total_cids': len(cid_data),
        'overall_no_supp_ops': float(overall_no_supp_ops),
        'overall_total_ops': float(overall_total_ops)
    }
}

output_file = f'sshve2_data_new_suppression_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(output_json, f, ensure_ascii=False, indent=2)

print(f"\n✅ Saved to: {output_file}")

# Verify sample MCID
sample_mcid = '851346684'
if sample_mcid in [c['cid'] for c in cid_data]:
    sample_cid_data = next(c for c in cid_data if c['cid'] == sample_mcid)
    print(f"\n" + "=" * 80)
    print(f"Verification - MCID {sample_mcid}:")
    print(f"  Merchant Name: {sample_cid_data['merchant_name']}")
    print(f"  Sourced GMS: {sample_cid_data['current_gms']:,.0f}")
    print(f"  SSHVE2 Suppression:")
    for cat, pct in sample_cid_data['sshve2_suppression'].items():
        print(f"    {cat}: {pct:.1f}%")
    print(f"  Forecast OPS: {sample_cid_data['forecast_ops']:,.0f}")
    print("=" * 80)

print("\n✨ Data rebuild with new suppression complete!")
print("=" * 80)
