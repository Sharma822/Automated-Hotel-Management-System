import sys
import pymysql

# MySQL Workbench configuration
DB_CONFIG = {
    'host': '127.0.0.1',
    'port': 3306,
    'user': 'root',
    'password': 'admin123',  # <-- Apna MySQL password yahan check/update karein
    'database': 'hotel_management_db',
    'autocommit': True,
    'cursorclass': pymysql.cursors.DictCursor
}

def get_connection():
    return pymysql.connect(**DB_CONFIG)

# 1. Test Minimum Balance Account Creation (Exp 1)
def test_create_account(acc_id, name, balance):
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.callproc('sp_create_guest_account', (acc_id, name, balance, ''))
            cursor.execute("SELECT @_sp_create_guest_account_3 AS status_msg;")
            res = cursor.fetchone()
            print(f"[Account Creation] ID: {acc_id} -> {res['status_msg']}")
        conn.close()
    except Exception as e:
        print(f"[Account Creation Error]: {e}")

# 2. Test Low Stock Report using Explicit Cursor (Exp 2)
def test_low_stock_report():
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.callproc('sp_generate_low_stock_report')
            rows = cursor.fetchall()
            print("\n--- LOW STOCK INVENTORY REPORT (CURSOR) ---")
            for r in rows:
                print(f"Item ID: {r['item_id']} | Name: {r['item_name']:<20} | Stock: {r['current_stock']} | Reorder: {r['reorder_level']}")
        conn.close()
    except Exception as e:
        print(f"[Cursor Report Error]: {e}")

# 3. Test Employee Bonus Function in SQL Query
def test_bonus_calculation():
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            query = """
                SELECT emp_id, emp_name, basic_salary, 
                       fn_calc_emp_bonus(basic_salary) AS bonus,
                       (basic_salary + fn_calc_emp_bonus(basic_salary)) AS total_salary
                FROM hotel_employees;
            """
            cursor.execute(query)
            rows = cursor.fetchall()
            print("\n--- EMPLOYEE BONUS REPORT (FUNCTION) ---")
            for r in rows:
                print(f"Emp ID: {r['emp_id']} | {r['emp_name']:<15} | Base: {r['basic_salary']} | Bonus: {r['bonus']} | Total: {r['total_salary']}")
        conn.close()
    except Exception as e:
        print(f"[Bonus Function Error]: {e}")

# 4. Test Room Booking Procedure with Transaction Management
def test_room_booking(guest_name, room_type_id, qty):
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.callproc('sp_process_room_booking', (guest_name, room_type_id, qty, 0, ''))
            cursor.execute("SELECT @_sp_process_room_booking_3 AS b_id, @_sp_process_room_booking_4 AS msg;")
            res = cursor.fetchone()
            print(f"\n[Booking Attempt] Guest: {guest_name} | ID: {res['b_id']} | Status: {res['msg']}")
        conn.close()
    except Exception as e:
        print(f"[Booking Error]: {e}")

if __name__ == '__main__':
    print("=== RUNNING HOTEL MANAGEMENT BACKEND TESTS ===")
    
    # Connection Check
    try:
        print("Connecting with PyMySQL driver...")
        conn = get_connection()
        print(">>> Database connected successfully! <<<\n")
        conn.close()
    except Exception as err:
        print(f"\nDATABASE CONNECTION FAILED: {err}")
        sys.exit(1)

    # 1. Minimum Balance Validation Test (Updated IDs)
    test_create_account(104, "Amit Sharma", 500.00)
    test_create_account(105, "Pooja Verma", 1500.00)

    # 2. Low Stock Explicit Cursor Report
    test_low_stock_report()

    # 3. Employee Bonus Function
    test_bonus_calculation()

    # 4. Transactional Room Booking
    test_room_booking("Sameer Khan", 1, 2)
    test_room_booking("Rohit Sen", 2, 5)

    print("\n=== ALL TESTS FINISHED ===")