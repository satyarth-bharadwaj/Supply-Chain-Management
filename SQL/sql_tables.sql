CREATE DATABASE abc_supermarket;
USE abc_supermarket;

CREATE TABLE sales (
    Sale_ID VARCHAR(10) PRIMARY KEY,
    Product_ID VARCHAR(10),
    Store_ID VARCHAR(10),
    Sale_Date DATE,
    Quantity_Sold INT,
    Revenue DECIMAL(10,2)
);

CREATE TABLE inventory (
    Product_ID VARCHAR(10),
    Store_ID VARCHAR(10),
    Warehouse_ID VARCHAR(10),
    Stock_Level INT,
    Reorder_Level INT,
    Last_Updated DATE,
    PRIMARY KEY (Product_ID, Store_ID)
);

CREATE TABLE suppliers (
    Supplier_ID VARCHAR(10) PRIMARY KEY,
    Supplier_Name VARCHAR(100),
    Product_ID VARCHAR(10),
    Lead_Time INT,
    Order_Frequency VARCHAR(20)
);


CREATE TABLE purchase_orders (
    Order_ID VARCHAR(10) PRIMARY KEY,
    Product_ID VARCHAR(10),
    Supplier_ID VARCHAR(10),
    Order_Date DATE,
    Quantity INT,
    Arrival_Date DATE
);

-- Dimension Tables
CREATE TABLE dim_product (
    Product_ID VARCHAR(10) PRIMARY KEY
);

CREATE TABLE dim_store (
    Store_ID VARCHAR(10) PRIMARY KEY
);

CREATE TABLE dim_supplier (
    Supplier_ID VARCHAR(10) PRIMARY KEY,
    Supplier_Name VARCHAR(100)
);

-- Fact Tables
CREATE TABLE fact_sales (
    Sale_ID VARCHAR(10) PRIMARY KEY,
    Product_ID VARCHAR(10),
    Store_ID VARCHAR(10),
    Sale_Date DATE,
    Quantity_Sold INT,
    Revenue DECIMAL(10,2),
    FOREIGN KEY (Product_ID) REFERENCES dim_product(Product_ID),
    FOREIGN KEY (Store_ID) REFERENCES dim_store(Store_ID)
);

CREATE TABLE fact_inventory (
    Product_ID VARCHAR(10),
    Store_ID VARCHAR(10),
    Warehouse_ID VARCHAR(10),
    Stock_Level INT,
    Reorder_Level INT,
    Last_Updated DATE,
    PRIMARY KEY (Product_ID, Store_ID, Warehouse_ID),
    FOREIGN KEY (Product_ID) REFERENCES dim_product(Product_ID),
    FOREIGN KEY (Store_ID) REFERENCES dim_store(Store_ID)
);

CREATE TABLE fact_purchase_orders (
    Order_ID VARCHAR(10) PRIMARY KEY,
    Product_ID VARCHAR(10),
    Supplier_ID VARCHAR(10),
    Order_Date DATE,
    Quantity INT,
    Arrival_Date DATE,
    FOREIGN KEY (Product_ID) REFERENCES dim_product(Product_ID),
    FOREIGN KEY (Supplier_ID) REFERENCES dim_supplier(Supplier_ID)
);

-- Insert Data into Dimension Tables
INSERT INTO dim_product (Product_ID)
SELECT DISTINCT Product_ID FROM sales;

INSERT INTO dim_store (Store_ID)
SELECT DISTINCT Store_ID FROM sales;

INSERT INTO dim_supplier (Supplier_ID, Supplier_Name)
SELECT DISTINCT Supplier_ID, Supplier_Name FROM suppliers;

-- Insert Data into Fact Tables
INSERT INTO fact_sales (Sale_ID, Product_ID, Store_ID, Sale_Date, Quantity_Sold, Revenue)
SELECT Sale_ID, Product_ID, Store_ID, Sale_Date, Quantity_Sold, Revenue FROM sales;

INSERT INTO fact_inventory (Product_ID, Store_ID, Warehouse_ID, Stock_Level, Reorder_Level, Last_Updated)
SELECT Product_ID, Store_ID, Warehouse_ID, Stock_Level, Reorder_Level, Last_Updated FROM inventory;

INSERT INTO fact_purchase_orders (Order_ID, Product_ID, Supplier_ID, Order_Date, Quantity, Arrival_Date)
SELECT Order_ID, Product_ID, Supplier_ID, Order_Date, Quantity, Arrival_Date FROM purchase_orders;

CREATE TABLE dim_date (
    Date_ID DATE PRIMARY KEY,
    Year INT NOT NULL,
    Month INT NOT NULL,
    Month_Name VARCHAR(15) NOT NULL,
    Quarter INT NOT NULL,
    Quarter_Name VARCHAR(10) NOT NULL,
    Week INT NOT NULL,
    Day INT NOT NULL,
    Day_Name VARCHAR(10) NOT NULL,
    Is_Weekend BOOLEAN NOT NULL
);

INSERT INTO dim_date (Date_ID, Year, Month, Month_Name, Quarter, Quarter_Name, Week, Day, Day_Name, Is_Weekend)
WITH RECURSIVE date_series AS (
    SELECT DATE('2020-01-01') AS Date_ID
    UNION ALL
    SELECT Date_ID + INTERVAL 1 DAY FROM date_series WHERE Date_ID < DATE('2030-12-31')
)
SELECT 
    Date_ID,
    YEAR(Date_ID) AS Year,
    MONTH(Date_ID) AS Month,
    MONTHNAME(Date_ID) AS Month_Name,
    QUARTER(Date_ID) AS Quarter,
    CASE 
        WHEN QUARTER(Date_ID) = 1 THEN 'Q1'
        WHEN QUARTER(Date_ID) = 2 THEN 'Q2'
        WHEN QUARTER(Date_ID) = 3 THEN 'Q3'
        ELSE 'Q4'
    END AS Quarter_Name,
    WEEK(Date_ID, 1) AS Week,
    DAY(Date_ID) AS Day,
    DAYNAME(Date_ID) AS Day_Name,
    CASE 
        WHEN DAYOFWEEK(Date_ID) IN (1,7) THEN TRUE 
        ELSE FALSE 
    END AS Is_Weekend
FROM date_series;

CREATE TABLE abc_supermarket.agg_sales_summary AS
SELECT 
    s.Product_ID,
    s.Store_ID,
    d.Sales_Month,
    SUM(s.Quantity_Sold) AS Total_Quantity_Sold,
    SUM(s.Revenue) AS Total_Revenue
FROM abc_supermarket.fact_sales s
JOIN abc_supermarket.dim_product p ON s.Product_ID = p.Product_ID
JOIN abc_supermarket.dim_store st ON s.Store_ID = st.Store_ID
JOIN (SELECT DISTINCT Sale_Date, DATE_FORMAT(Sale_Date, '%Y-%m') AS Sales_Month FROM abc_supermarket.fact_sales) d 
    ON s.Sale_Date = d.Sale_Date
GROUP BY s.Product_ID, p.Product_ID, s.Store_ID, d.Sales_Month;

CREATE TABLE abc_supermarket.agg_store_performance AS
SELECT 
    s.Store_ID,
    COUNT(DISTINCT s.Sale_ID) AS Total_Transactions,
    SUM(s.Quantity_Sold) AS Total_Quantity_Sold,
    SUM(s.Revenue) AS Total_Revenue,
    ROUND(AVG(s.Revenue), 2) AS Avg_Revenue_Per_Transaction
FROM abc_supermarket.fact_sales s
GROUP BY s.Store_ID;

CREATE TABLE abc_supermarket.agg_supplier_performance AS
SELECT 
    po.Supplier_ID,
    COUNT(po.Order_ID) AS Total_Orders,
    SUM(po.Quantity) AS Total_Quantity_Ordered,
    ROUND(AVG(DATEDIFF(po.Arrival_Date, po.Order_Date)), 2) AS Avg_Lead_Time
FROM abc_supermarket.fact_purchase_orders po
JOIN abc_supermarket.dim_supplier s ON po.Supplier_ID = s.Supplier_ID
GROUP BY po.Supplier_ID, s.Supplier_ID;

CREATE TABLE abc_supermarket.agg_inventory_summary AS
SELECT 
    i.Product_ID,
    i.Store_ID,
    i.Warehouse_ID,
    SUM(i.Stock_Level) AS Total_Stock,
    SUM(i.Reorder_Level) AS Total_Reorder_Level,
    CASE 
        WHEN SUM(i.Stock_Level) < SUM(i.Reorder_Level) THEN 'Restock Needed'
        ELSE 'Sufficient Stock'
    END AS Stock_Status
FROM abc_supermarket.fact_inventory i
JOIN abc_supermarket.dim_product p ON i.Product_ID = p.Product_ID
GROUP BY i.Product_ID, p.Product_ID, i.Store_ID, i.Warehouse_ID;

CREATE TABLE abc_supermarket.agg_monthly_revenue AS
SELECT 
    DATE_FORMAT(Sale_Date, '%Y-%m') AS Sales_Month,
    SUM(Revenue) AS Total_Revenue
FROM abc_supermarket.fact_sales
GROUP BY Sales_Month
ORDER BY Sales_Month;


