"""
Check JSON output for specific MCIDs
"""
import json

json_file = 'sshve2_data_complete_20260318_214749.json'
with open(json_file, 'r', encoding='utf-8') as f:
    data = json.load(f)

# Check MCID 851346684
mcid = '851346684'
mcid_data = next((c for c in data['cids'] if c['cid'] == mcid), None)

if mcid_data:
    print(f"MCID {mcid}:")
    print(f"  Merchant Name: {mcid_data['merchant_name']}")
    print(f"  Sourced GMS (Act): {mcid_data['current_gms']:,.0f}")
    print(f"  Target GMS: {mcid_data['target_gms']:,.0f}")
    print(f"  Gap: {mcid_data['gap']:,.0f}")
else:
    print(f"MCID {mcid} not found")

# Check total non-zero GMSs
non_zero = [c for c in data['cids'] if c['current_gms'] > 0]
print(f"\nTotal MCIDs with non-zero Sourced GMS: {len(non_zero)} / {len(data['cids'])}")

# Show top 5
print(f"\nTop 5 MCIDs by Sourced GMS:")
sorted_cids = sorted(data['cids'], key=lambda x: x['current_gms'], reverse=True)
for c in sorted_cids[:5]:
    print(f"  {c['cid']}: {c['current_gms']:,.0f}")
