#!/usr/bin/env python3
"""Find the MCID with extremely large data"""

import ijson
import json
from decimal import Decimal

class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super().default(obj)

suppression_file = 'data/suppression_raw_by_mcid.json'

print("Scanning for large MCIDs...")
large_mcids = []

with open(suppression_file, 'rb') as f:
    parser = ijson.kvitems(f, '')
    
    for mcid, data in parser:
        # Estimate size
        json_str = json.dumps({mcid: data}, ensure_ascii=False, cls=DecimalEncoder)
        size_mb = len(json_str.encode('utf-8')) / (1024 * 1024)
        
        if size_mb > 90:
            large_mcids.append((mcid, size_mb, len(data)))
            print(f"MCID: {mcid}, Size: {size_mb:.2f} MB, Items: {len(data)}")

print(f"\nFound {len(large_mcids)} large MCIDs")
