"""
SSHVE2 Bridge Plan Dashboard - Complete Version
- Filter by PF = "Total CE" only
- Use SSHVE2 Suppression data
- Calculate Promotion OPS (Forecast, Target, vs Target)
- Support Team/Mgr bulk input
"""

import pandas as pd
import json
from datetime import datetime

print("=" * 70)
print("SSHVE2 Bridge Plan Dashboard Generator - Complete Version")
print("=" * 70)
print()

# Suppression Coefficients
COEFFICIENTS = {
    "No suppression": 0.5343,
    "OOS": 0.2807,
    "VRP Missing": 0.0963,
    "Price Error": 0.275,
    "Others": 0.1801
}

print("Step 1: Loading data files...")
print("-" * 70)

# Load Target data
print("Loading Target data...")
target_df = pd.read_excel(r"C:\Users\murakei\Desktop\SSHVE2\Dashboard\raw\Suppression\SSHVE2_BySeller_Target.xlsx")
print(f"  ✅ Target: {len(target_df)} MCIDs")

# Load Sourcing data (for Total CE filtering)
print("Loading Sourcing data...")
sourcing_df = pd.read_csv(r"C:\Users\murakei\Desktop\SSHVE2\Sourcing\Tracking\Sourcing_data_raw_Sourcing更新.csv", low_memory=False)
# Filter for Total CE only
sourcing_ce = sourcing_df[sourcing_df['pf'] == 'Total CE'].copy()
print(f"  ✅ Sourcing (Total CE): {len(sourcing_ce)} ASINs")

# Load SSHVE2 Suppression data
print("Loading SSHVE2 Suppression data...")
sshve2_supp_df = pd.read_csv(r"C:\Users\murakei\Desktop\SSHVE2\Dashboard\raw\Suppression\SSHVE2_ByASIN_Suppression_raw.txt", sep='\t')
# Filter for Total CE only
sshve2_supp_ce = sshve2_supp_df[sshve2_supp_df['pf'] == 'Total CE'].copy()
print(f"  ✅ SSHVE2 Suppression (Total CE): {len(sshve2_supp_ce)} records")

# Load SSHVE1 Suppression data (for Target calculation)
print("Loading SSHVE1 Suppression data...")
sshve1_supp_df = pd.read_csv(r"C:\Users\murakei\Desktop\SSHVE2\Dashboard\raw\Suppression\SSHVE1_BySuppressionReason_Percentage.csv")
print(f"  ✅ SSHVE1 Suppression: {len(sshve1_supp_df)} records")

print()
print("Step 2: Processing SSHVE2 Suppression data by MCID...")
print("-" * 70)

# Aggregate SSHVE2 Suppression by MCID
sshve2_by_mcid = sshve2_supp_ce.groupby('merchant_customer_id').agg({
    'cat_pct_no_suppression': 'mean',
    'cat_pct_oos': 'mean',
    'cat_pct_vrp_missing': 'mean',
    'cat_pct_price_error': 'mean',
    'cat_pct_others': 'mean'
}).reset_index()

print(f"  ✅ Aggregated {len(sshve2_by_mcid)} MCIDs")

print()
print("Step 3: Processing data for each MCID...")
print("-" * 70)

all_data = []
processed_count = 0

for idx, row in target_df.iterrows():
    if idx % 500 == 0:
        print(f"  Processing {idx}/{len(target_df)}...")
    
    mcid = int(row['mcid'])
    mcid_str = str(mcid)
    
    # Basic info
    alias = str(row.get('Alias', ''))
    mgr = str(row.get('Mgr', ''))
    team = str(row.get('Team', ''))
    current_gms = float(row.get('total_t30d_gms_BAU', 0))
    target_gms = float(row.get('T30 GMS Target', 0))
    
    # Get Total CE sourcing data for this MCID
    mcid_sourcing_ce = sourcing_ce[sourcing_ce['mcid'] == mcid]
    
    # Skip if no Total CE data
    if len(mcid_sourcing_ce) == 0:
        continue
    
    # Event participation (Total CE only)
    event_participation = {
        'sshve1_flag': {'asin_count': int(len(mcid_sourcing_ce[mcid_sourcing_ce.get('sshve1_flag', '') == 'Y']))},
        't365_flag': {'asin_count': int(len(mcid_sourcing_ce[mcid_sourcing_ce.get('t365_flag', '') == 'Y']))}
    }
    
    # Get SSHVE2 Suppression data for this MCID
    sshve2_supp = sshve2_by_mcid[sshve2_by_mcid['merchant_customer_id'] == mcid]
    
    if len(sshve2_supp) > 0:
        s2 = sshve2_supp.iloc[0]
        sshve2_suppression = {
            'No suppression': float(s2.get('cat_pct_no_suppression', 0) * 100) if pd.notna(s2.get('cat_pct_no_suppression')) else 0,
            'OOS': float(s2.get('cat_pct_oos', 0) * 100) if pd.notna(s2.get('cat_pct_oos')) else 0,
            'VRP Missing': float(s2.get('cat_pct_vrp_missing', 0) * 100) if pd.notna(s2.get('cat_pct_vrp_missing')) else 0,
            'Price Error': float(s2.get('cat_pct_price_error', 0) * 100) if pd.notna(s2.get('cat_pct_price_error')) else 0,
            'Others': float(s2.get('cat_pct_others', 0) * 100) if pd.notna(s2.get('cat_pct_others')) else 0
        }
    else:
        sshve2_suppression = {
            'No suppression': 0, 'OOS': 0, 'VRP Missing': 0, 'Price Error': 0, 'Others': 0
        }
    
    # Get SSHVE1 Suppression data for this MCID
    sshve1_supp = sshve1_supp_df[sshve1_supp_df['merchant_customer_id'] == mcid]
    
    if len(sshve1_supp) > 0:
        s1 = sshve1_supp.iloc[0]
        sshve1_suppression = {
            'No suppression': float(s1.get('current_cat_pct_no_suppression', 0) * 100) if pd.notna(s1.get('current_cat_pct_no_suppression')) else 0,
            'OOS': float(s1.get('current_cat_pct_oos', 0) * 100) if pd.notna(s1.get('current_cat_pct_oos')) else 0,
            'VRP Missing': float(s1.get('current_cat_pct_vrp_missing', 0) * 100) if pd.notna(s1.get('current_cat_pct_vrp_missing')) else 0,
            'Price Error': float(s1.get('current_cat_pct_price_error', 0) * 100) if pd.notna(s1.get('current_cat_pct_price_error')) else 0,
            'Others': float(s1.get('current_cat_pct_others', 0) * 100) if pd.notna(s1.get('current_cat_pct_others')) else 0
        }
    else:
        sshve1_suppression = {
            'No suppression': 0, 'OOS': 0, 'VRP Missing': 0, 'Price Error': 0, 'Others': 0
        }
    
    # Calculate Promotion OPS - Forecast (SS2 Suppressionベース)
    forecast_ops = 0
    for cat, pct in sshve2_suppression.items():
        forecast_ops += current_gms * (pct / 100) * COEFFICIENTS[cat]
    
    # Calculate Promotion OPS - Target (SS1 Suppressionベース)
    target_ops = 0
    for cat, pct in sshve1_suppression.items():
        target_ops += target_gms * (pct / 100) * COEFFICIENTS[cat]
    
    # vs Target
    vs_target_ops = forecast_ops - target_ops
    
    data = {
        'cid': mcid_str,
        'alias': alias,
        'mgr': mgr,
        'team': team,
        'current_gms': current_gms,
        'target_gms': target_gms,
        'gap': target_gms - current_gms,
        'event_participation': event_participation,
        'sshve2_suppression': sshve2_suppression,
        'sshve1_suppression': sshve1_suppression,
        'forecast_ops': forecast_ops,
        'target_ops': target_ops,
        'vs_target_ops': vs_target_ops
    }
    
    all_data.append(data)
    processed_count += 1

print(f"  ✅ Processed {processed_count} MCIDs with Total CE data")

print()
print("Step 4: Saving data to JSON...")
print("-" * 70)

output_json = f"sshve2_data_v2_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
with open(output_json, 'w', encoding='utf-8') as f:
    json.dump({'cids': all_data, 'coefficients': COEFFICIENTS}, f, ensure_ascii=False)

print(f"  ✅ Saved to {output_json}")

print()
print("=" * 70)
print(f"✨ Data processing complete! Processed {len(all_data)} MCIDs")
print("=" * 70)
print()
print(f"Output file: {output_json}")
print()
