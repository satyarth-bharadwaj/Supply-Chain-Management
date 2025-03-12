import pandas as pd
from sqlalchemy import create_engine

# MySQL connection details
db_engine = create_engine("mysql+mysqlconnector://root:@127.0.0.1:3306/abc_supermarket")

# Load Excel file
file_path = "ABC-SuperMarketData.xlsx"

# Read Sales Data from Sheet 1
sales_df = pd.read_excel(file_path, sheet_name="Sales Data")  
sales_df.to_sql("sales", con=db_engine, if_exists="append", index=False)

# Read Inventory Data from Sheet 2
inventory_df = pd.read_excel(file_path, sheet_name="Inventory Data")
inventory_df.to_sql("inventory", con=db_engine, if_exists="append", index=False)

# Read Supplier Data from Sheet 3
suppliers_df = pd.read_excel(file_path, sheet_name="Supplier Data")
suppliers_df.to_sql("suppliers", con=db_engine, if_exists="append", index=False)

# Read Purchase Orders Data from Sheet 4
purchase_orders_df = pd.read_excel(file_path, sheet_name="Purchase Orders")
purchase_orders_df.to_sql("purchase_orders", con=db_engine, if_exists="append", index=False)

print("Data successfully loaded into MySQL!")
