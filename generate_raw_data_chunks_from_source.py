#!/usr/bin/env python3
"""
元のRawファイルを直接読み込んでMCID単位にチャンク化
Sourcing/Suppressionそれぞれのファイルを処理
"""

import pandas as pd
import json
import os
from pathlib import Path

def process_sourcing_to_chunks(max_chunk_size_mb=90):
    """Process Sourcing raw data directly to chunks."""
    print("\n" + "="*60)
    print("📊 Sourcing Rawデータを処理中...")
    print("="*60)
    
    sourcing_path = Path("C:/Users/murakei/Desktop/SSHVE2/Sourcing/Tracking/Sourcing_data_raw_Sourcing更新.csv")
    
    if not sourcing_path.exists():
        print(f"⚠️ Sourcingファイルが見つかりません: {sourcing_path}")
        return 0, 0, []
    
    df = pd.read_csv(sourcing_path, encoding='utf-8-sig')
    
    output_dir = Path('data/sourcing_raw_chunks')
    output_dir.mkdir(parents=True, exist_ok=True)
    
    chunk_index = {}
    chunk_num = 0
    current_chunk = {}
    mcid_count = 0
    excluded_mcids = []
    chunk_size = 500  # 500 MCIDs per chunk
    
    for mcid, group in df.groupby('mcid'):
        mcid_str = str(int(mcid)) if pd.notna(mcid) else 'unknown'
        mcid_count += 1
        
        # Build records for this MCID - preserve ALL columns from original file
        # Replace NaN with None (null in JSON) for valid JSON output
        records = group.where(pd.notna(group), None).to_dict('records')
        
        # Check if this single MCID is too large
        single_mcid_json = json.dumps({mcid_str: records}, ensure_ascii=False, indent=2)
        single_size_mb = len(single_mcid_json.encode('utf-8')) / (1024 * 1024)
        
        if single_size_mb > max_chunk_size_mb:
            excluded_mcids.append({
                'mcid': mcid_str,
                'size_mb': round(single_size_mb, 2),
                'item_count': len(records)
            })
            print(f"  [EXCLUDED] MCID {mcid_str}: {single_size_mb:.2f} MB, {len(records)} items")
            continue
        
        # Add to current chunk
        current_chunk[mcid_str] = records
        chunk_index[mcid_str] = chunk_num
        
        # Save chunk when it reaches target size
        if len(current_chunk) >= chunk_size:
            chunk_file = output_dir / f'chunk_{chunk_num}.json'
            with open(chunk_file, 'w', encoding='utf-8') as f:
                json.dump(current_chunk, f, ensure_ascii=False, indent=2)
            
            file_size_mb = os.path.getsize(chunk_file) / (1024 * 1024)
            print(f"  Chunk {chunk_num}: {len(current_chunk)} MCIDs, {file_size_mb:.2f} MB")
            
            chunk_num += 1
            current_chunk = {}
    
    # Save remaining data
    if current_chunk:
        chunk_file = output_dir / f'chunk_{chunk_num}.json'
        with open(chunk_file, 'w', encoding='utf-8') as f:
            json.dump(current_chunk, f, ensure_ascii=False, indent=2)
        
        file_size_mb = os.path.getsize(chunk_file) / (1024 * 1024)
        print(f"  Chunk {chunk_num}: {len(current_chunk)} MCIDs, {file_size_mb:.2f} MB")
        chunk_num += 1
    
    # Save index file
    index_file = output_dir / 'index.json'
    with open(index_file, 'w', encoding='utf-8') as f:
        json.dump(chunk_index, f, ensure_ascii=False)
    
    # Save excluded MCIDs list
    if excluded_mcids:
        excluded_file = output_dir / 'excluded.json'
        with open(excluded_file, 'w', encoding='utf-8') as f:
            json.dump(excluded_mcids, f, ensure_ascii=False, indent=2)
        print(f"\n[WARN] {len(excluded_mcids)} MCIDs excluded (too large)")
        print(f"[WARN] Excluded list: {excluded_file}")
    
    print(f"\n[OK] Created {chunk_num} chunks")
    print(f"[OK] Index file: {index_file}")
    print(f"[OK] Total MCIDs processed: {mcid_count}")
    print(f"[OK] MCIDs included: {mcid_count - len(excluded_mcids)}")
    
    return chunk_num, mcid_count, excluded_mcids

def process_suppression_to_chunks(max_chunk_size_mb=90):
    """Process Suppression raw data directly to chunks."""
    print("\n" + "="*60)
    print("📊 Suppression Rawデータを処理中...")
    print("="*60)
    
    suppression_path = Path("C:/Users/murakei/Desktop/SSHVE2/Dashboard/raw/Suppression/SSHVE2_ByASIN_Suppression_raw_Final_item.tsv")
    
    if not suppression_path.exists():
        print(f"⚠️ Suppressionファイルが見つかりません: {suppression_path}")
        return 0, 0, []
    
    df = pd.read_csv(suppression_path, sep='\t', encoding='utf-8-sig')
    
    output_dir = Path('data/suppression_raw_chunks')
    output_dir.mkdir(parents=True, exist_ok=True)
    
    chunk_index = {}
    chunk_num = 0
    mcid_count = 0
    excluded_mcids = []
    
    for mcid, group in df.groupby('merchant_customer_id'):
        mcid_str = str(int(mcid)) if pd.notna(mcid) else 'unknown'
        mcid_count += 1
        
        # Build records for this MCID - preserve ALL columns from original file
        # Replace NaN with None (null in JSON) for valid JSON output
        records = group.where(pd.notna(group), None).to_dict('records')
        
        # Check if this single MCID is too large
        single_mcid_json = json.dumps({mcid_str: records}, ensure_ascii=False, indent=2)
        single_size_mb = len(single_mcid_json.encode('utf-8')) / (1024 * 1024)
        
        if single_size_mb > max_chunk_size_mb:
            excluded_mcids.append({
                'mcid': mcid_str,
                'size_mb': round(single_size_mb, 2),
                'item_count': len(records)
            })
            print(f"  [EXCLUDED] MCID {mcid_str}: {single_size_mb:.2f} MB, {len(records)} items")
            continue
        
        # Each MCID gets its own chunk (1 MCID per chunk)
        chunk_file = output_dir / f'chunk_{chunk_num}.json'
        with open(chunk_file, 'w', encoding='utf-8') as f:
            json.dump({mcid_str: records}, f, ensure_ascii=False, indent=2)
        
        chunk_index[mcid_str] = chunk_num
        chunk_num += 1
        
        if mcid_count % 1000 == 0:
            print(f"  Processed {mcid_count} MCIDs...")
    
    # Save index file
    index_file = output_dir / 'index.json'
    with open(index_file, 'w', encoding='utf-8') as f:
        json.dump(chunk_index, f, ensure_ascii=False)
    
    # Save excluded MCIDs list
    if excluded_mcids:
        excluded_file = output_dir / 'excluded.json'
        with open(excluded_file, 'w', encoding='utf-8') as f:
            json.dump(excluded_mcids, f, ensure_ascii=False, indent=2)
        print(f"\n[WARN] {len(excluded_mcids)} MCIDs excluded (too large)")
        print(f"[WARN] Excluded list: {excluded_file}")
    
    print(f"\n[OK] Created {chunk_num} chunks")
    print(f"[OK] Index file: {index_file}")
    print(f"[OK] Total MCIDs processed: {mcid_count}")
    print(f"[OK] MCIDs included: {mcid_count - len(excluded_mcids)}")
    
    return chunk_num, mcid_count, excluded_mcids

def main():
    print("\n" + "="*60)
    print("Raw Data Chunk Generator (Direct from Source)")
    print("="*60)
    
    # Process both datasets directly from source files
    sourcing_chunks, sourcing_total, sourcing_excluded = process_sourcing_to_chunks()
    suppression_chunks, suppression_total, suppression_excluded = process_suppression_to_chunks()
    
    print("\n" + "="*60)
    print("Summary")
    print("="*60)
    print(f"Sourcing: {sourcing_total} MCIDs -> {sourcing_chunks} chunks ({len(sourcing_excluded)} excluded)")
    print(f"Suppression: {suppression_total} MCIDs -> {suppression_chunks} chunks ({len(suppression_excluded)} excluded)")
    print("\n[OK] All data split successfully!")
    print("\nNext steps:")
    print("1. Commit and push to GitHub")
    print("2. Test download functionality on GitHub Pages")

if __name__ == '__main__':
    main()
