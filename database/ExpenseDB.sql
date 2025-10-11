CREATE DATABASE IF NOT EXISTS ExpenseDB;
USE ExpenseDB;

CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100),
    email VARCHAR(100) UNIQUE,
    password VARCHAR(200)
);

CREATE TABLE expenses (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    title VARCHAR(100),
    amount DECIMAL(10,2),
    category VARCHAR(50),
    date DATE,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
