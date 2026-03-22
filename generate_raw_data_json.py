"""
ASIN単位のRawデータをJSON形式に変換
セラーごとにフィルタリングしてダウンロードできるようにする
"""

import pandas as pd
import json
from pathlib import Path

def process_sourcing_data():
    """Process Sourcing raw data."""
    print("📊 Sourcing Rawデータを処理中...")
    
    sourcing_path = Path("C:/Users/murakei/Desktop/SSHVE2/Sourcing/Tracking/Sourcing_data_raw_Sourcing更新.csv")
    
    if not sourcing_path.exists():
        print(f"⚠️ Sourcingファイルが見つかりません: {sourcing_path}")
        return {}
    
    df = pd.read_csv(sourcing_path, encoding='utf-8-sig')
    
    # MCIDでグループ化
    sourcing_by_mcid = {}
    
    for mcid, group in df.groupby('mcid'):
        mcid_str = str(int(mcid)) if pd.notna(mcid) else 'unknown'
        
        records = []
        for _, row in group.iterrows():
            records.append({
                'asin': str(row.get('asin.1', '')),
                'item_name': str(row.get('item_name', '')),
                'adopted_flag': str(row.get('SSHVE2_Adopted Flag', '')),
                'sourced_flag': str(row.get('SSHVE2_SourcedFlag', '')),
                'pf': str(row.get('pf', '')),
                'gl': str(row.get('gl', '')),
                'total_gms': float(row.get('total_t30d_gms_BAU', 0)) if pd.notna(row.get('total_t30d_gms_BAU')) else 0,
                'priority': str(row.get('priority', '')),
            })
        
        sourcing_by_mcid[mcid_str] = records
    
    print(f"✅ Sourcing: {len(sourcing_by_mcid)} MCIDs処理完了")
    return sourcing_by_mcid

def process_suppression_data():
    """Process Suppression raw data."""
    print("📊 Suppression Rawデータを処理中...")
    
    suppression_path = Path("C:/Users/murakei/Desktop/SSHVE2/Dashboard/raw/Suppression/SSHVE2_ByASIN_Suppression_raw_Final_item.tsv")
    
    if not suppression_path.exists():
        print(f"⚠️ Suppressionファイルが見つかりません: {suppression_path}")
        return {}
    
    df = pd.read_csv(suppression_path, sep='\t', encoding='utf-8-sig')
    
    # MCIDでグループ化
    suppression_by_mcid = {}
    
    for mcid, group in df.groupby('merchant_customer_id'):
        mcid_str = str(int(mcid)) if pd.notna(mcid) else 'unknown'
        
        records = []
        for _, row in group.iterrows():
            records.append({
                'asin': str(row.get('asin', '')),
                'item_name': str(row.get('item_name', '')),
                'suppression_reason': str(row.get('cleaned_suppression_reason', '')),
                'suppression_category': str(row.get('suppression_category_large', '')),
                'pf': str(row.get('pf', '')),
                't30d_ops': float(row.get('t30d_ops', 0)) if pd.notna(row.get('t30d_ops')) else 0,
                't30d_units': float(row.get('t30d_units', 0)) if pd.notna(row.get('t30d_units')) else 0,
            })
        
        suppression_by_mcid[mcid_str] = records
    
    print(f"✅ Suppression: {len(suppression_by_mcid)} MCIDs処理完了")
    return suppression_by_mcid

def main():
    """Generate JSON files for raw data download."""
    
    # Process both datasets
    sourcing_data = process_sourcing_data()
    suppression_data = process_suppression_data()
    
    # Save to JSON files
    output_dir = Path('data')
    output_dir.mkdir(exist_ok=True)
    
    sourcing_output = output_dir / 'sourcing_raw_by_mcid.json'
    with open(sourcing_output, 'w', encoding='utf-8') as f:
        json.dump(sourcing_data, f, ensure_ascii=False, indent=2)
    print(f"✅ Sourcing JSONファイル生成: {sourcing_output}")
    
    suppression_output = output_dir / 'suppression_raw_by_mcid.json'
    with open(suppression_output, 'w', encoding='utf-8') as f:
        json.dump(suppression_data, f, ensure_ascii=False, indent=2)
    print(f"✅ Suppression JSONファイル生成: {suppression_output}")
    
    print()
    print("🎉 完了！")
    print(f"📊 Sourcing: {len(sourcing_data)} MCIDs")
    print(f"📊 Suppression: {len(suppression_data)} MCIDs")

if __name__ == '__main__':
    main()
