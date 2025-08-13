import pandas as pd
import os

# Create sample data
data = {
    'region': ['North', 'South', 'East', 'West', 'Central'],
    'sales': [125000, 98000, 156000, 87000, 134000],
    'quarter': ['Q1', 'Q1', 'Q1', 'Q1', 'Q1'],
    'year': [2025, 2025, 2025, 2025, 2025]
}

df = pd.DataFrame(data)

# Create Excel file
output_path = '/Users/nobeltsegai/Documents/Seo-dev/datavein-work/root/tests/sample_data/sales.xlsx'
df.to_excel(output_path, index=False)
print(f"Created Excel file: {output_path}")

# Also create a parquet file
parquet_path = '/Users/nobeltsegai/Documents/Seo-dev/datavein-work/root/tests/sample_data/sales.parquet'
df.to_parquet(parquet_path, index=False)
print(f"Created Parquet file: {parquet_path}")
