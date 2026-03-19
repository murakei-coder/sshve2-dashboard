import pandas as pd
import json
from datetime import datetime

print("SSHVE2 Dashboard Generator - Filter-First Approach")
print("=" * 60)

# Load data
print("Loading data...")
target_df = pd.read_excel(r"C:\Users\murakei\Desktop\SSHVE2\Dashboard\raw\Suppression\SSHVE2_BySeller_Target.xlsx")
sourcing_df = pd.read_csv(r"C:\Users\murakei\Desktop\SSHVE2\Sourcing\Tracking\Sourcing_data_raw_Sourcing更新.csv", low_memory=False)
suppression_df = pd.read_csv(r"C:\Users\murakei\Desktop\SSHVE2\Dashboard\raw\Suppression\SSHVE1_BySuppressionReason_Percentage.csv")

print(f"Loaded {len(target_df)} MCIDs")

# Save as JSON
output_file = f"sshve2_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
print(f"Saving to {output_file}...")

all_data = []
for idx, row in target_df.iterrows():
    if idx % 500 == 0:
        print(f"  Processing {idx}/{len(target_df)}...")
    
    mcid = int(row["mcid"])
    mcid_str = str(mcid)
    
    data = {
        "cid": mcid_str,
        "alias": str(row.get("Alias", "")),
        "mgr": str(row.get("Mgr", "")),
        "team": str(row.get("Team", "")),
        "current_gms": float(row.get("total_t30d_gms_BAU", 0)),
        "target_gms": float(row.get("T30 GMS Target", 0)),
        "gap": float(row.get("T30 GMS Target", 0)) - float(row.get("total_t30d_gms_BAU", 0))
    }
    
    mcid_sourcing = sourcing_df[sourcing_df["mcid"] == mcid]
    data["event_participation"] = {
        "sshve1_flag": {"asin_count": int(len(mcid_sourcing[mcid_sourcing.get("sshve1_flag", "") == "Y"]))},
        "t365_flag": {"asin_count": int(len(mcid_sourcing[mcid_sourcing.get("t365_flag", "") == "Y"]))}
    }
    
    supp_row = suppression_df[suppression_df["merchant_customer_id"] == mcid]
    if len(supp_row) > 0:
        s = supp_row.iloc[0]
        data["suppression_breakdown"] = {
            "No suppression": {"percentage": float(s.get("current_cat_pct_no_suppression", 0) * 100) if pd.notna(s.get("current_cat_pct_no_suppression")) else 0},
            "OOS": {"percentage": float(s.get("current_cat_pct_oos", 0) * 100) if pd.notna(s.get("current_cat_pct_oos")) else 0},
            "VRP Missing": {"percentage": float(s.get("current_cat_pct_vrp_missing", 0) * 100) if pd.notna(s.get("current_cat_pct_vrp_missing")) else 0},
            "Price Error": {"percentage": float(s.get("current_cat_pct_price_error", 0) * 100) if pd.notna(s.get("current_cat_pct_price_error")) else 0},
            "Others": {"percentage": float(s.get("current_cat_pct_others", 0) * 100) if pd.notna(s.get("current_cat_pct_others")) else 0}
        }
    else:
        data["suppression_breakdown"] = {
            "No suppression": {"percentage": 0},
            "OOS": {"percentage": 0},
            "VRP Missing": {"percentage": 0},
            "Price Error": {"percentage": 0},
            "Others": {"percentage": 0}
        }
    
    all_data.append(data)

with open(output_file, "w", encoding="utf-8") as f:
    json.dump({"cids": all_data}, f, ensure_ascii=False)

print(f"Saved {len(all_data)} MCIDs to {output_file}")
print("Done!")
