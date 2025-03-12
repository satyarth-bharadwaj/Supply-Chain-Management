import pandas as pd
import numpy as np
from faker import Faker

# Initialize Faker for random names
fake = Faker()

# Constants
NUM_PRODUCTS = 50
NUM_STORES = 10
NUM_WAREHOUSES = 5
NUM_SUPPLIERS = 100
NUM_SALES = 10000
NUM_PURCHASE_ORDERS = 1000

# Generate unique IDs
product_ids = [f"P{i:03d}" for i in range(1, NUM_PRODUCTS + 1)]
store_ids = [f"S{i:03d}" for i in range(101, 101 + NUM_STORES)]
warehouse_ids = [f"W{i:03d}" for i in range(1, NUM_WAREHOUSES + 1)]
supplier_ids = [f"SUP{i:03d}" for i in range(1, NUM_SUPPLIERS + 1)]

# Generate Unit Prices for each product
unit_prices = {product_id: np.random.randint(50, 500) for product_id in product_ids}

# Generate Sales Data
sales_data = {
    "Sale_ID": [f"SL{i:05d}" for i in range(1, NUM_SALES + 1)],
    "Product_ID": np.random.choice(product_ids, NUM_SALES),
    "Store_ID": np.random.choice(store_ids, NUM_SALES),
    "Sale_Date": pd.date_range(start="2024-01-01", end="2024-03-31", periods=NUM_SALES).date,  # Keep only date
    "Quantity_Sold": np.random.randint(1, 100, NUM_SALES),
}
sales_df = pd.DataFrame(sales_data)
# Calculate Revenue as Quantity_Sold * Unit_Price
sales_df["Revenue"] = sales_df.apply(lambda row: row["Quantity_Sold"] * unit_prices[row["Product_ID"]], axis=1)

# Generate Inventory Data
inventory_data = {
    "Product_ID": np.repeat(product_ids, NUM_STORES),
    "Store_ID": np.tile(store_ids, NUM_PRODUCTS),
    "Warehouse_ID": np.random.choice(warehouse_ids, NUM_PRODUCTS * NUM_STORES),
    "Stock_Level": np.random.randint(0, 500, NUM_PRODUCTS * NUM_STORES),
    "Reorder_Level": 100,
    "Last_Updated": pd.date_range(start="2024-01-01", end="2024-03-31", periods=NUM_PRODUCTS * NUM_STORES).date,  # Keep only date
}
inventory_df = pd.DataFrame(inventory_data)

# Generate Supplier Data
supplier_data = {
    "Supplier_ID": supplier_ids,
    "Supplier_Name": [fake.company() for _ in range(NUM_SUPPLIERS)],
    "Product_ID": np.random.choice(product_ids, NUM_SUPPLIERS),
    "Lead_Time": np.random.randint(3, 10, NUM_SUPPLIERS),
    "Order_Frequency": np.random.choice(["Weekly", "Biweekly"], NUM_SUPPLIERS),
}
suppliers_df = pd.DataFrame(supplier_data)

# Generate Purchase Orders
purchase_order_data = {
    "Order_ID": [f"PO{i:05d}" for i in range(1, NUM_PURCHASE_ORDERS + 1)],
    "Product_ID": np.random.choice(product_ids, NUM_PURCHASE_ORDERS),
    "Supplier_ID": np.random.choice(supplier_ids, NUM_PURCHASE_ORDERS),
    "Order_Date": pd.date_range(start="2024-01-01", end="2024-03-31", periods=NUM_PURCHASE_ORDERS).date,  # Keep only date
    "Quantity": np.random.randint(50, 500, NUM_PURCHASE_ORDERS),
}
purchase_orders_df = pd.DataFrame(purchase_order_data)
purchase_orders_df["Arrival_Date"] = purchase_orders_df.apply(
    lambda row: row["Order_Date"] + pd.Timedelta(days=suppliers_df.loc[suppliers_df["Supplier_ID"] == row["Supplier_ID"], "Lead_Time"].values[0]), axis=1
)

# Save to Excel
excel_path = "C:/Users/satya/OneDrive/Desktop/ADMM/ADMM Projects/Project 2 - SupplyChainInventoryManagement/abc_supermarket_revenue_proportional.xlsx"
with pd.ExcelWriter(excel_path, datetime_format="YYYY-MM-DD") as writer:  # Format dates without time
    sales_df.to_excel(writer, sheet_name="Sales Data", index=False)
    inventory_df.to_excel(writer, sheet_name="Inventory Data", index=False)
    suppliers_df.to_excel(writer, sheet_name="Supplier Data", index=False)
    purchase_orders_df.to_excel(writer, sheet_name="Purchase Orders", index=False)

print(f"Dataset generated and saved to '{excel_path}'.")