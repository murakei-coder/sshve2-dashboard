#!/usr/bin/env python3
"""
Split large raw data JSON files into smaller chunks for GitHub Pages deployment.
This script splits sourcing_raw_by_mcid.json and suppression_raw_by_mcid.json
into multiple smaller files to avoid GitHub's 100MB file size limit.
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
    If a single MCID exceeds max_chunk_size_mb, it will be split into its own file.
    
    Args:
        input_file: Path to input JSON file
        output_dir: Directory to save chunked files
        chunk_size: Number of MCIDs per chunk
        data_type: 'sourcing' or 'suppression'
        max_chunk_size_mb: Maximum chunk size in MB (default 90MB to stay under 100MB limit)
    """
    print(f"\n{'='*60}")
    print(f"Processing {data_type} data...")
    print(f"{'='*60}")
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"Reading {input_file} in streaming mode...")
    
    # First pass: count MCIDs and build index
    import ijson
    
    chunk_index = {}
    chunk_num = 0
    current_chunk = {}
    mcid_count = 0
    large_mcid_count = 0
    
    with open(input_file, 'rb') as f:
        parser = ijson.kvitems(f, '')
        
        for mcid, data in parser:
            mcid_count += 1
            
            # Check if adding this MCID would exceed size limit
            # Estimate size by converting to JSON string
            test_chunk = {**current_chunk, mcid: data}
            test_json = json.dumps(test_chunk, ensure_ascii=False, cls=DecimalEncoder)
            test_size_mb = len(test_json.encode('utf-8')) / (1024 * 1024)
            
            # If this single MCID is too large, save it separately
            single_mcid_json = json.dumps({mcid: data}, ensure_ascii=False, cls=DecimalEncoder)
            single_size_mb = len(single_mcid_json.encode('utf-8')) / (1024 * 1024)
            
            if single_size_mb > max_chunk_size_mb:
                # Save current chunk if not empty
                if current_chunk:
                    chunk_file = os.path.join(output_dir, f'chunk_{chunk_num}.json')
                    with open(chunk_file, 'w', encoding='utf-8') as cf:
                        json.dump(current_chunk, cf, ensure_ascii=False, cls=DecimalEncoder)
                    
                    file_size_mb = os.path.getsize(chunk_file) / (1024 * 1024)
                    print(f"  Chunk {chunk_num}: {len(current_chunk)} MCIDs, {file_size_mb:.2f} MB")
                    chunk_num += 1
                    current_chunk = {}
                
                # Save large MCID separately
                chunk_file = os.path.join(output_dir, f'chunk_{chunk_num}.json')
                with open(chunk_file, 'w', encoding='utf-8') as cf:
                    json.dump({mcid: data}, cf, ensure_ascii=False, cls=DecimalEncoder)
                
                file_size_mb = os.path.getsize(chunk_file) / (1024 * 1024)
                print(f"  Chunk {chunk_num}: 1 MCID (LARGE), {file_size_mb:.2f} MB")
                chunk_index[mcid] = chunk_num
                chunk_num += 1
                large_mcid_count += 1
                continue
            
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
    
    print(f"\n[OK] Created {chunk_num} chunks")
    print(f"[OK] Index file: {index_file}")
    print(f"[OK] Total MCIDs: {mcid_count}")
    if large_mcid_count > 0:
        print(f"[WARN] {large_mcid_count} MCIDs were too large and saved separately")
    
    return chunk_num, mcid_count

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
    sourcing_chunks, sourcing_total = split_json_data_streaming(
        sourcing_file,
        'data/sourcing_raw_chunks',
        500,
        'Sourcing'
    )
    
    # Split Suppression data (1 MCID per chunk - some individual MCIDs have extremely large data)
    suppression_chunks, suppression_total = split_json_data_streaming(
        suppression_file,
        'data/suppression_raw_chunks',
        1,
        'Suppression'
    )
    
    print("\n" + "="*60)
    print("Summary")
    print("="*60)
    print(f"Sourcing: {sourcing_total} MCIDs -> {sourcing_chunks} chunks")
    print(f"Suppression: {suppression_total} MCIDs -> {suppression_chunks} chunks")
    print("\n[OK] All data split successfully!")
    print("\nNext steps:")
    print("1. Update HTML file to use chunked data")
    print("2. Delete original large JSON files")
    print("3. Commit and push to GitHub")

if __name__ == '__main__':
    main()
