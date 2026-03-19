"""
Check all sheets in Excel file
"""
import pandas as pd

raw_file = r'C:\Users\murakei\Desktop\SSHVE2\Dashboard\raw\CID ASIN SSHVE2_ALL PF.xlsx'
print(f"Loading: {raw_file}\n")

# Get all sheet names
xl_file = pd.ExcelFile(raw_file)
print(f"Total sheets: {len(xl_file.sheet_names)}")
print("\nSheet names:")
for i, sheet in enumerate(xl_file.sheet_names, 1):
    print(f"  {i}. '{sheet}'")

# Load first sheet with more details
print(f"\n{'='*80}")
print(f"Loading first sheet: '{xl_file.sheet_names[0]}'")
df = pd.read_excel(raw_file, sheet_name=xl_file.sheet_names[0])
print(f"Rows: {len(df)}, Columns: {len(df.columns)}")
print(f"\nColumns: {list(df.columns)}")
print(f"\nFirst 2 rows:")
print(df.head(2))

# If there are multiple sheets, check the second one
if len(xl_file.sheet_names) > 1:
    print(f"\n{'='*80}")
    print(f"Loading second sheet: '{xl_file.sheet_names[1]}'")
    df2 = pd.read_excel(raw_file, sheet_name=xl_file.sheet_names[1])
    print(f"Rows: {len(df2)}, Columns: {len(df2.columns)}")
    print(f"\nColumns: {list(df2.columns)}")
    print(f"\nFirst 2 rows:")
    print(df2.head(2))
