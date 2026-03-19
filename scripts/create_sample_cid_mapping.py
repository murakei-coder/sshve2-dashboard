"""
Script to create sample CID mapping Excel file.
"""

import pandas as pd
from pathlib import Path

# Create sample CID mapping data
data = {
    'CID': ['CID001', 'CID002', 'CID003', 'CID004', 'CID005', 
            'CID006', 'CID007', 'CID008', 'CID009', 'CID010'],
    'Alias': ['田中太郎', '佐藤花子', '鈴木一郎', '高橋美咲', '渡辺健太',
              '伊藤さくら', '山本大輔', '中村優子', '小林誠', '加藤愛'],
    'Mgr': ['山田マネージャー', '山田マネージャー', '佐々木マネージャー', '佐々木マネージャー', '佐々木マネージャー',
            '田村マネージャー', '田村マネージャー', '田村マネージャー', '木村マネージャー', '木村マネージャー'],
    'Team': ['東京チーム', '東京チーム', '東京チーム', '東京チーム', '東京チーム',
             '大阪チーム', '大阪チーム', '大阪チーム', '大阪チーム', '大阪チーム']
}

df = pd.DataFrame(data)

# Create data directory if it doesn't exist
output_dir = Path('data')
output_dir.mkdir(exist_ok=True)

# Save to Excel
output_file = output_dir / 'sample_cid_mapping.xlsx'
df.to_excel(output_file, sheet_name='Sheet1', index=False, engine='openpyxl')

print(f"✅ Created sample CID mapping file: {output_file}")
