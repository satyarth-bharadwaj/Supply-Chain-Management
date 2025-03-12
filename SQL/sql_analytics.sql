-- Query to find Stock Level is less than Reorder Level
SELECT Product_ID, Store_ID, Stock_Level, Reorder_Level
FROM fact_inventory
WHERE Stock_Level < Reorder_Level;

-- Query to find highest Total Sales product wise
SELECT Product_ID, SUM(Quantity_Sold) AS Total_Sales
FROM fact_sales
WHERE Sale_Date IS NOT NULL
AND Sale_Date >= (SELECT DATE_ADD(MAX(Sale_Date), INTERVAL -3 MONTH) FROM fact_sales)
GROUP BY Product_ID
ORDER BY Total_Sales DESC;

-- Average Lead Time for each supply
SELECT Supplier_ID, AVG(DATEDIFF(Arrival_Date, Order_Date)) AS Avg_Lead_Time
FROM fact_purchase_orders
GROUP BY Supplier_ID
ORDER BY Avg_Lead_Time DESC;