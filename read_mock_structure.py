import pandas as pd
import openpyxl

# Read the mock file
wb = openpyxl.load_workbook(r'C:\Users\murakei\Desktop\Kiro_Mock.xlsx')
ws = wb.active

print("=" * 80)
print("Mock File Structure Analysis")
print("=" * 80)

# Print first 15 rows
print("\nFirst 15 rows:")
for i, row in enumerate(ws.iter_rows(values_only=True), 1):
    print(f"Row {i}: {row}")
    if i >= 15:
        break

# Try to read as DataFrame
print("\n" + "=" * 80)
print("Reading as DataFrame:")
print("=" * 80)

df = pd.read_excel(r'C:\Users\murakei\Desktop\Kiro_Mock.xlsx', header=None)
print(f"\nShape: {df.shape}")
print(f"\nFirst 10 rows:\n{df.head(10)}")
