USE mamaearth_db;

-- Drop existing tables if they conflict (so you can recreate them perfectly)
DROP TABLE IF EXISTS orders;
DROP TABLE IF EXISTS products;
DROP TABLE IF EXISTS customers;

-- 1. Create the customers table exactly as specified
CREATE TABLE customers (
    customer_id VARCHAR(10) PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    city VARCHAR(50) NOT NULL,
    city_tier INT NOT NULL,
    signup_date DATE NOT NULL,
    acquisition_source VARCHAR(20) NOT NULL
);

-- 2. Create the products table exactly as specified
CREATE TABLE products (
    product_id VARCHAR(10) PRIMARY KEY,
    product_name VARCHAR(100) NOT NULL,
    category VARCHAR(30) NOT NULL,
    price DECIMAL(10,2) NOT NULL
);

-- 3. Create the orders table exactly as specified
CREATE TABLE orders (
    order_id VARCHAR(10) PRIMARY KEY,
    customer_id VARCHAR(10) NOT NULL,
    product_id VARCHAR(10) NOT NULL,
    order_date DATE NOT NULL,
    quantity INT NOT NULL,
    discount_pct INT,      -- Deliberately allows NULL
    payment_method VARCHAR(10) NOT NULL,
    rating INT,            -- Deliberately allows NULL
    returned INT NOT NULL DEFAULT 0,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
    FOREIGN KEY (product_id) REFERENCES products(product_id)
);
