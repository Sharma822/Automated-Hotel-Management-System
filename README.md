# 🏨 Automated Hotel Management System with Enterprise PL/SQL Logic and Streamlit Web Interface

An enterprise-grade, database-driven hospitality operations system developed using **MySQL 8.0 (PL/SQL)**, **Python**, and a **Streamlit Web UI**.

---

## 📌 Project Overview
* **Candidate Name:** Vikram
* **Roll No / UID:** 26MCD10072
* **Class:** MCD-2(A)
* **Academic Supervisor:** Ms. Winky Bhatia (Assistant Professor)
* **Department:** Department of Computer Applications, University Institute of Computing (UIC)
* **Institution:** Chandigarh University

---

## 🛠️ Tech Stack & Architecture
* **Relational Database:** MySQL 8.0
* **Backend Logic:** PL/SQL (Stored Procedures, Stored Functions, Explicit Cursors, Triggers, ACID Transactions)
* **Database Driver:** PyMySQL
* **Frontend Web Framework:** Streamlit
* **Version Control:** Git & GitHub

---

## 🎯 Implemented Modules & Core Logic

### 1. Module 1: Guest Account Creation (`sp_create_guest_account`)
* **Validation Rule:** Enforces a mandatory minimum opening deposit balance of INR 1,000.00.
* Prevents duplicate account creation and returns real-time feedback through `OUT` parameters.

### 2. Module 2: Low-Stock Inventory Auditing (`sp_generate_low_stock_report`)
* Uses an **Explicit Cursor** (`cur_low_stock`) with an active `CONTINUE HANDLER FOR NOT FOUND`.
* Filters consumable items (Towels, Water Bottles, Toiletries) whose available stock has dipped below their specified reorder threshold.

### 3. Module 3: Staff Payroll Bonus Engine (`fn_calc_emp_bonus`)
* A **Deterministic Stored Function** that dynamically calculates staff bonus incentives based on monthly salary slabs:
  * `< INR 20,000`: 15% Bonus
  * `INR 20,000 - INR 40,000`: 12% Bonus
  * `> INR 40,000`: 10% Bonus

### 4. Module 4: Concurrent Room Booking System (`sp_process_room_booking`)
* Fully **ACID-compliant transaction management** with `START TRANSACTION`, `COMMIT`, and `ROLLBACK`.
* Employs pessimistic row-level locking (`FOR UPDATE`) to prevent race conditions during high-concurrency booking attempts.
* Employs an `EXIT HANDLER FOR SQLEXCEPTION` to automatically roll back transactions in the event of unexpected database errors.

### 5. Module 5: Room & Stock Administration
* Dynamic room catalog management from the web UI.
* Enables adding new room tiers, refilling depleted room stock, and cascading room deletions.

---

## 📋 Database Schema

* `guest_accounts` — Customer profiles and deposit ledger.
* `hotel_inventory` — Consumables tracking with automated reorder levels.
* `hotel_employees` — Staff payroll records and designations.
* `hotel_rooms` — Room categories, active inventory, and night tariffs.
* `room_bookings` — Transaction log of confirmed reservations.

---

## 🚀 Execution & Setup Guide

### 1. Database Initialization
1. Open **MySQL Workbench**.
2. Open and execute the complete script file: `sql1.sql`.
3. Verify that the `hotel_management_db` database, tables, and routines are created.

### 2. Configure Local Database Credentials
Ensure database credentials in `frontend_app.py` match your local MySQL configuration:
```python
DB_CONFIG = {
    'host': '127.0.0.1',
    'port': 3306,
    'user': 'root',
    'password': 'admin123',
    'database': 'hotel_management_db',
    'autocommit': True,
    'cursorclass': pymysql.cursors.DictCursor
}
