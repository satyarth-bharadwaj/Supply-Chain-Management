import pandas as pd
import os

# Define file paths
raw_file_path = "C:/Users/satya/OneDrive/Desktop/ADMM/ADMM Projects/Project 2 - SupplyChainInventoryManagement/raw_data.xlsx"
cleaned_file_path = "C:/Users/satya/OneDrive/Desktop/ADMM/ADMM Projects/Project 2 - SupplyChainInventoryManagement/cleaned_data.xlsx"
csv_output_path = "C:/Users/satya/OneDrive/Desktop/ADMM/ADMM Projects/Project 2 - SupplyChainInventoryManagement/csv/"

# Load raw data
sales_df = pd.read_excel(raw_file_path, sheet_name="sales")
inventory_df = pd.read_excel(raw_file_path, sheet_name="inventory")
suppliers_df = pd.read_excel(raw_file_path, sheet_name="suppliers")
purchase_orders_df = pd.read_excel(raw_file_path, sheet_name="purchase_orders")

# Create output directory if it doesn't exist
os.makedirs(csv_output_path, exist_ok=True)

# Remove duplicates
sales_df.drop_duplicates(inplace=True)
inventory_df.drop_duplicates(inplace=True)
suppliers_df.drop_duplicates(inplace=True)
purchase_orders_df.drop_duplicates(inplace=True)

# Handle missing values
sales_df.fillna({'Quantity_Sold': 0, 'Revenue': 0}, inplace=True)
inventory_df.fillna({'Stock_Level': 0, 'Reorder_Level': 0}, inplace=True)
purchase_orders_df.fillna({'Quantity': 0}, inplace=True)

# Standardize Product_ID format
for df in [sales_df, inventory_df, suppliers_df, purchase_orders_df]:
    if 'Product_ID' in df.columns:
        df['Product_ID'] = df['Product_ID'].astype(str).str.upper()

# Ensure referential integrity
valid_products = set(inventory_df['Product_ID']).intersection(set(suppliers_df['Product_ID']))
sales_df = sales_df[sales_df['Product_ID'].isin(valid_products)]
purchase_orders_df = purchase_orders_df[purchase_orders_df['Product_ID'].isin(valid_products)]

# Save cleaned data to a new Excel file
with pd.ExcelWriter(cleaned_file_path) as writer:
    sales_df.to_excel(writer, sheet_name="sales", index=False)
    inventory_df.to_excel(writer, sheet_name="inventory", index=False)
    suppliers_df.to_excel(writer, sheet_name="suppliers", index=False)
    purchase_orders_df.to_excel(writer, sheet_name="purchase_orders", index=False)

# Save cleaned data as CSV files for MySQL loading
sales_df.to_csv(os.path.join(csv_output_path, "cleaned_sales.csv"), index=False)
inventory_df.to_csv(os.path.join(csv_output_path, "cleaned_inventory.csv"), index=False)
suppliers_df.to_csv(os.path.join(csv_output_path, "cleaned_suppliers.csv"), index=False)
purchase_orders_df.to_csv(os.path.join(csv_output_path, "cleaned_purchase_orders.csv"), index=False)

print("ETL process completed. Cleaned data saved successfully.")