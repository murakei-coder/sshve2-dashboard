#!/usr/bin/env python3
"""
Split large raw data JSON files into smaller chunks for GitHub Pages deployment.
Excludes MCIDs that are too large (>90MB) and creates a separate list of excluded MCIDs.
"""

import json
import os
from pathlib import Path
from decimal import Decimal

class DecimalEncoder(json.JSONEncoder):
    """Custom JSON encoder to handle Decimal types"""
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super().default(obj)

def split_json_data_streaming(input_file, output_dir, chunk_size, data_type, max_chunk_size_mb=90):
    """
    Split a large JSON file into smaller chunks using streaming to avoid memory issues.
    MCIDs that exceed max_chunk_size_mb are excluded and tracked separately.
    """
    print(f"\n{'='*60}")
    print(f"Processing {data_type} data...")
    print(f"{'='*60}")
    
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"Reading {input_file} in streaming mode...")
    
    import ijson
    
    chunk_index = {}
    chunk_num = 0
    current_chunk = {}
    mcid_count = 0
    excluded_mcids = []
    
    with open(input_file, 'rb') as f:
        parser = ijson.kvitems(f, '')
        
        for mcid, data in parser:
            mcid_count += 1
            
            # Check if this single MCID is too large
            single_mcid_json = json.dumps({mcid: data}, ensure_ascii=False, cls=DecimalEncoder)
            single_size_mb = len(single_mcid_json.encode('utf-8')) / (1024 * 1024)
            
            if single_size_mb > max_chunk_size_mb:
                excluded_mcids.append({
                    'mcid': mcid,
                    'size_mb': round(single_size_mb, 2),
                    'item_count': len(data)
                })
                print(f"  [EXCLUDED] MCID {mcid}: {single_size_mb:.2f} MB, {len(data)} items")
                continue
            
            # Check if adding this MCID would exceed size limit
            test_chunk = {**current_chunk, mcid: data}
            test_json = json.dumps(test_chunk, ensure_ascii=False, cls=DecimalEncoder)
            test_size_mb = len(test_json.encode('utf-8')) / (1024 * 1024)
            
            # If adding this MCID would exceed limit, save current chunk first
            if test_size_mb > max_chunk_size_mb and current_chunk:
                chunk_file = os.path.join(output_dir, f'chunk_{chunk_num}.json')
                with open(chunk_file, 'w', encoding='utf-8') as cf:
                    json.dump(current_chunk, cf, ensure_ascii=False, cls=DecimalEncoder)
                
                file_size_mb = os.path.getsize(chunk_file) / (1024 * 1024)
                print(f"  Chunk {chunk_num}: {len(current_chunk)} MCIDs, {file_size_mb:.2f} MB")
                
                chunk_num += 1
                current_chunk = {}
            
            # Add MCID to current chunk
            current_chunk[mcid] = data
            chunk_index[mcid] = chunk_num
            
            # When chunk reaches target size, save it
            if len(current_chunk) >= chunk_size:
                chunk_file = os.path.join(output_dir, f'chunk_{chunk_num}.json')
                with open(chunk_file, 'w', encoding='utf-8') as cf:
                    json.dump(current_chunk, cf, ensure_ascii=False, cls=DecimalEncoder)
                
                file_size_mb = os.path.getsize(chunk_file) / (1024 * 1024)
                print(f"  Chunk {chunk_num}: {len(current_chunk)} MCIDs, {file_size_mb:.2f} MB")
                
                chunk_num += 1
                current_chunk = {}
    
    # Save remaining data
    if current_chunk:
        chunk_file = os.path.join(output_dir, f'chunk_{chunk_num}.json')
        with open(chunk_file, 'w', encoding='utf-8') as cf:
            json.dump(current_chunk, cf, ensure_ascii=False, cls=DecimalEncoder)
        
        file_size_mb = os.path.getsize(chunk_file) / (1024 * 1024)
        print(f"  Chunk {chunk_num}: {len(current_chunk)} MCIDs, {file_size_mb:.2f} MB")
        chunk_num += 1
    
    # Save index file
    index_file = os.path.join(output_dir, 'index.json')
    with open(index_file, 'w', encoding='utf-8') as f:
        json.dump(chunk_index, f, ensure_ascii=False)
    
    # Save excluded MCIDs list
    if excluded_mcids:
        excluded_file = os.path.join(output_dir, 'excluded.json')
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
    print("Raw Data JSON Splitter")
    print("="*60)
    
    # Check if input files exist
    sourcing_file = 'data/sourcing_raw_by_mcid.json'
    suppression_file = 'data/suppression_raw_by_mcid.json'
    
    if not os.path.exists(sourcing_file):
        print(f"[ERROR] Error: {sourcing_file} not found")
        return
    
    if not os.path.exists(suppression_file):
        print(f"[ERROR] Error: {suppression_file} not found")
        return
    
    # Split Sourcing data (500 MCIDs per chunk)
    sourcing_chunks, sourcing_total, sourcing_excluded = split_json_data_streaming(
        sourcing_file,
        'data/sourcing_raw_chunks',
        500,
        'Sourcing'
    )
    
    # Split Suppression data (1 MCID per chunk with size check)
    suppression_chunks, suppression_total, suppression_excluded = split_json_data_streaming(
        suppression_file,
        'data/suppression_raw_chunks',
        1,
        'Suppression'
    )
    
    print("\n" + "="*60)
    print("Summary")
    print("="*60)
    print(f"Sourcing: {sourcing_total} MCIDs -> {sourcing_chunks} chunks ({len(sourcing_excluded)} excluded)")
    print(f"Suppression: {suppression_total} MCIDs -> {suppression_chunks} chunks ({len(suppression_excluded)} excluded)")
    print("\n[OK] All data split successfully!")
    print("\nNext steps:")
    print("1. Update HTML file to use chunked data")
    print("2. Delete original large JSON files")
    print("3. Commit and push to GitHub")

if __name__ == '__main__':
    main()
