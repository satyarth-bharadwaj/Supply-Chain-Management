# =========================== 📌 Import Libraries ===========================
import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt
import seaborn as sns
from sqlalchemy import create_engine
from statsmodels.tsa.arima.model import ARIMA
from sklearn.linear_model import LinearRegression
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

# ✅ Fix Joblib warning (set CPU limit)
os.environ["LOKY_MAX_CPU_COUNT"] = "4"

# ✅ Connect to MySQL Database
engine = create_engine("mysql+mysqlconnector://root:@127.0.0.1/abc_supermarket")

# ✅ Function to Fetch Data Safely
def fetch_data(query, name="Data"):
    try:
        df = pd.read_sql(query, con=engine)
        if df.empty:
            print(f"⚠ No data found for {name}. Check your database.")
        return df
    except Exception as e:
        print(f"❌ Error fetching {name}: {e}")
        return pd.DataFrame()

# =========================== 📌 Demand Forecasting ===========================
query_sales = """
    SELECT DATE_FORMAT(Sale_Date, '%Y-%m') AS Month, SUM(Quantity_Sold) AS Quantity_Sold
    FROM fact_sales
    GROUP BY Month
    ORDER BY Month;
"""
monthly_sales = fetch_data(query_sales, "Sales Data")

if not monthly_sales.empty and len(monthly_sales) >= 6:
    # ✅ Convert Month to DateTime & Set Index
    monthly_sales['Month'] = pd.to_datetime(monthly_sales['Month'])
    monthly_sales.set_index('Month', inplace=True)

    # ✅ ARIMA Forecast
    try:
        model = ARIMA(monthly_sales['Quantity_Sold'], order=(5, 1, 0))
        model_fit = model.fit()
        arima_forecast = model_fit.forecast(steps=1).iloc[0]
    except Exception as e:
        print(f"❌ ARIMA Error: {e}")
        arima_forecast = None

    # ✅ Linear Regression Forecast
    try:
        X = np.arange(len(monthly_sales)).reshape(-1, 1)
        y = monthly_sales['Quantity_Sold'].values
        model_lr = LinearRegression()
        model_lr.fit(X, y)
        next_month = np.array([[len(monthly_sales)]])
        linear_forecast = model_lr.predict(next_month)[0]
    except Exception as e:
        print(f"❌ Linear Regression Error: {e}")
        linear_forecast = None

    # ✅ Plot Forecast
    plt.figure(figsize=(10, 5))
    plt.plot(monthly_sales.index, monthly_sales['Quantity_Sold'], marker='o', label='Actual Sales')
    plt.axvline(monthly_sales.index[-1], color='gray', linestyle='--', label='Forecast Start')

    if arima_forecast:
        plt.scatter(monthly_sales.index[-1] + pd.DateOffset(months=1), arima_forecast, color='red', label='ARIMA Forecast')
    if linear_forecast:
        plt.scatter(monthly_sales.index[-1] + pd.DateOffset(months=1), linear_forecast, color='blue', label='Linear Forecast')

    plt.xlabel("Month")
    plt.ylabel("Quantity Sold")
    plt.title("Monthly Sales & Forecasting")
    plt.legend()
    plt.show()

# =========================== 📌 Reorder Point Calculation ===========================
query_inventory = "SELECT Product_ID, Stock_Level, Reorder_Level FROM fact_inventory;"
inventory_data = fetch_data(query_inventory, "Inventory Data")

query_demand = """
    SELECT Product_ID, AVG(Quantity_Sold) AS Daily_Demand
    FROM fact_sales
    WHERE Sale_Date >= DATE_SUB(CURDATE(), INTERVAL 90 DAY)
    GROUP BY Product_ID;
"""
demand_data = fetch_data(query_demand, "Demand Data")

query_supplier = """
    SELECT Product_ID, AVG(DATEDIFF(Arrival_Date, Order_Date)) AS Avg_Lead_Time
    FROM fact_purchase_orders
    WHERE Arrival_Date IS NOT NULL
    GROUP BY Product_ID;
"""
lead_time_data = fetch_data(query_supplier, "Supplier Data")

# ✅ Merge Data
reorder_data = inventory_data.merge(demand_data, on="Product_ID", how="left") \
                             .merge(lead_time_data, on="Product_ID", how="left")

# ✅ Handle Missing Values
reorder_data.fillna(0, inplace=True)
import pandas as pd
from sqlalchemy import create_engine

# ✅ Connect to MySQL Database
engine = create_engine("mysql+mysqlconnector://root:@127.0.0.1/abc_supermarket")

# ✅ Fetch Inventory Data
query_inventory = "SELECT Product_ID, Store_ID, Stock_Level FROM fact_inventory;"
inventory_data = pd.read_sql(query_inventory, con=engine)

# ✅ Fetch Daily Demand (Last 90 days)
query_demand = """
    SELECT Product_ID, AVG(Quantity_Sold) AS Daily_Demand
    FROM fact_sales
    WHERE Sale_Date >= DATE_SUB(CURDATE(), INTERVAL 90 DAY)
    GROUP BY Product_ID;
"""
demand_data = pd.read_sql(query_demand, con=engine)

# ✅ Fetch Supplier Lead Time
query_supplier = """
    SELECT Product_ID, AVG(DATEDIFF(Arrival_Date, Order_Date)) AS Lead_Time
    FROM fact_purchase_orders
    WHERE Arrival_Date IS NOT NULL
    GROUP BY Product_ID;
"""
lead_time_data = pd.read_sql(query_supplier, con=engine)

# ✅ Merge Data
reorder_data = inventory_data.merge(demand_data, on="Product_ID", how="left") \
                             .merge(lead_time_data, on="Product_ID", how="left")

# ✅ Handle Missing Values
reorder_data.fillna(0, inplace=True)

# ✅ Compute Safety Stock (95% Confidence Level)
reorder_data["Safety_Stock"] = 1.65 * reorder_data["Daily_Demand"].std()

# ✅ Calculate Reorder Point (ROP)
reorder_data["Reorder_Point"] = (reorder_data["Daily_Demand"] * reorder_data["Lead_Time"]) + reorder_data["Safety_Stock"]

# ✅ Identify Products to Reorder
products_to_reorder = reorder_data[reorder_data["Stock_Level"] <= reorder_data["Reorder_Point"]]

# ✅ Insert Reorder Point Data into MySQL Table
reorder_data.to_sql("fact_reorder_points", con=engine, if_exists="replace", index=False)

# ✅ Show Output
print("\n✅ Reorder Point Calculated & Stored in Database Successfully!")
print(products_to_reorder[['Product_ID', 'Store_ID', 'Stock_Level', 'Reorder_Point']])


# =========================== 📌 Supplier Performance Analysis ===========================
query_supplier_perf = """
    SELECT Supplier_ID, AVG(DATEDIFF(Arrival_Date, Order_Date)) AS Avg_Lead_Time, COUNT(Order_ID) AS Order_Frequency
    FROM fact_purchase_orders
    WHERE Arrival_Date IS NOT NULL
    GROUP BY Supplier_ID;
"""
supplier_data = fetch_data(query_supplier_perf, "Supplier Performance Data")

if not supplier_data.empty:
    # ✅ Standardize Data
    scaler = StandardScaler()
    supplier_scaled = scaler.fit_transform(supplier_data[['Avg_Lead_Time', 'Order_Frequency']])

    # ✅ Apply K-Means Clustering
    try:
        kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)
        supplier_data["Cluster"] = kmeans.fit_predict(supplier_scaled)
    except Exception as e:
        print(f"❌ Clustering Error: {e}")
        supplier_data["Cluster"] = None

    # ✅ Visualize Clusters
    plt.figure(figsize=(8, 6))
    sns.scatterplot(data=supplier_data, x='Avg_Lead_Time', y='Order_Frequency', hue='Cluster', palette='viridis', s=100)
    plt.xlabel("Average Lead Time (Days)")
    plt.ylabel("Order Frequency")
    plt.title("Supplier Performance Clustering")
    plt.legend(title="Cluster")
    plt.show()

    print("\n📊 Supplier Performance Clustering Results:")
    print(supplier_data)
