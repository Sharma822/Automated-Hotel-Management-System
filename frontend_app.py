import streamlit as st
import pymysql

# Page Configuration
st.set_page_config(page_title="Hotel Management System", page_icon="🏨", layout="wide")

st.title("🏨 Hotel Management & Booking System")
st.caption("PL/SQL & Python Integration (Stored Procedures, Cursors, Functions, ACID Transactions)")

# Database Configuration
DB_CONFIG = {
    'host': '127.0.0.1',
    'port': 3306,
    'user': 'root',
    'password': 'admin123',  # <-- Apna password check karein
    'database': 'hotel_management_db',
    'autocommit': True,
    'cursorclass': pymysql.cursors.DictCursor
}

def get_connection():
    return pymysql.connect(**DB_CONFIG)

# Dynamic Room Fetching for Dropdowns
def get_room_types():
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute("SELECT room_type_id, room_type_name, available_stock, price_per_night FROM hotel_rooms;")
            rooms = cursor.fetchall()
        conn.close()
        return rooms
    except Exception:
        return []

# Create Navigation Tabs (Naya Tab 5 add kiya gaya hai)
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "💳 Guest Account (Exp 1)", 
    "📦 Low Stock Inventory (Exp 2)", 
    "💰 Employee Bonus (Function)", 
    "🛎️ Room Booking (Procedure & ACID)",
    "⚙️ Manage Rooms (Add/Delete/Reset)"
])

# -----------------------------------------------------------------------------
# TAB 1: Minimum Balance Validation
# -----------------------------------------------------------------------------
with tab1:
    st.subheader("Experiment 1: Guest Account Creation with Min. Balance Validation")
    st.info("Rule: Account opening balance must be at least INR 1,000.00")
    
    with st.form("account_form"):
        col1, col2, col3 = st.columns(3)
        with col1:
            acc_id = st.number_input("Account ID", min_value=1, step=1, value=201)
        with col2:
            guest_name = st.text_input("Guest Name", value="Aakash Sharma")
        with col3:
            balance = st.number_input("Opening Balance (INR)", min_value=0.0, step=100.0, value=1200.0)
            
        submit_acc = st.form_submit_button("Create Account")

    if submit_acc:
        try:
            conn = get_connection()
            with conn.cursor() as cursor:
                cursor.callproc('sp_create_guest_account', (acc_id, guest_name, balance, ''))
                cursor.execute("SELECT @_sp_create_guest_account_3 AS status_msg;")
                res = cursor.fetchone()
                msg = res['status_msg']
                if "SUCCESS" in msg:
                    st.success(msg)
                else:
                    st.error(msg)
            conn.close()
        except Exception as e:
            st.error(f"Database Error: {e}")

# -----------------------------------------------------------------------------
# TAB 2: Low Stock Inventory (Explicit Cursor)
# -----------------------------------------------------------------------------
with tab2:
    st.subheader("Experiment 2: Low-Stock Inventory Report (Explicit Cursor)")
    st.write("Generates list of consumable items whose current stock is lower than the reorder level.")
    
    if st.button("Generate Inventory Report"):
        try:
            conn = get_connection()
            with conn.cursor() as cursor:
                cursor.callproc('sp_generate_low_stock_report')
                rows = cursor.fetchall()
                if rows:
                    st.dataframe(rows, use_container_width=True)
                else:
                    st.warning("All inventory items are currently above reorder levels.")
            conn.close()
        except Exception as e:
            st.error(f"Error fetching report: {e}")

# -----------------------------------------------------------------------------
# TAB 3: Employee Bonus (User-Defined Function)
# -----------------------------------------------------------------------------
with tab3:
    st.subheader("Module 3: Employee Bonus Calculation (Stored Function)")
    st.write("Calculates staff bonus dynamically based on basic salary slabs via `fn_calc_emp_bonus()`.")
    
    if st.button("Load Staff Bonus Details"):
        try:
            conn = get_connection()
            with conn.cursor() as cursor:
                query = """
                    SELECT emp_id AS 'Employee ID', 
                           emp_name AS 'Name', 
                           job_role AS 'Role', 
                           basic_salary AS 'Base Salary', 
                           fn_calc_emp_bonus(basic_salary) AS 'Bonus', 
                           (basic_salary + fn_calc_emp_bonus(basic_salary)) AS 'Total Payout' 
                    FROM hotel_employees;
                """
                cursor.execute(query)
                rows = cursor.fetchall()
                st.dataframe(rows, use_container_width=True)
            conn.close()
        except Exception as e:
            st.error(f"Error: {e}")

# -----------------------------------------------------------------------------
# TAB 4: Room Booking Transaction (Stored Procedure)
# -----------------------------------------------------------------------------
with tab4:
    st.subheader("Module 4: Room Booking Transaction (Commit & Rollback)")
    st.write("Ensures transactional consistency, updates inventory, and locks rows against concurrency.")
    
    available_rooms = get_room_types()
    
    if not available_rooms:
        st.warning("Database me koi room types nahi mile. Kripya pehle 'Manage Rooms' tab se room add karein.")
    else:
        with st.form("booking_form"):
            col1, col2, col3 = st.columns(3)
            with col1:
                b_guest = st.text_input("Customer Name", value="Karan Patel")
            with col2:
                room_type = st.selectbox(
                    "Room Type", 
                    options=available_rooms, 
                    format_func=lambda x: f"{x['room_type_name']} (Stock: {x['available_stock']}, Price: {x['price_per_night']})"
                )
            with col3:
                room_qty = st.number_input("Number of Rooms Needed", min_value=1, max_value=20, value=1)
                
            submit_booking = st.form_submit_button("Confirm Booking")

        if submit_booking:
            try:
                conn = get_connection()
                with conn.cursor() as cursor:
                    cursor.callproc('sp_process_room_booking', (b_guest, room_type['room_type_id'], room_qty, 0, ''))
                    cursor.execute("SELECT @_sp_process_room_booking_3 AS b_id, @_sp_process_room_booking_4 AS msg;")
                    res = cursor.fetchone()
                    
                    if res['b_id'] and res['b_id'] > 0:
                        st.success(f"{res['msg']} (Booking ID: #{res['b_id']})")
                    else:
                        st.error(res['msg'])
                conn.close()
            except Exception as e:
                st.error(f"Transaction Error: {e}")

# -----------------------------------------------------------------------------
# TAB 5: Manage Hotel Rooms (Add / Delete / Refill Stock)
# -----------------------------------------------------------------------------
with tab5:
    st.subheader("Room Management & Stock Controller")
    st.write("Yahan se aap naye rooms add kar sakte hain, stock badha sakte hain ya room delete kar sakte hain.")

    col_add, col_del = st.columns(2)

    # 1. Naya Room Add karna ya Stock Update karna
    with col_add:
        st.markdown("### ➕ Add or Update Room Type")
        with st.form("add_room_form"):
            new_room_id = st.number_input("Room Type ID", min_value=1, step=1, value=3)
            new_room_name = st.text_input("Room Name", value="Executive Suite")
            new_room_stock = st.number_input("Initial / Added Stock", min_value=1, step=1, value=10)
            new_room_price = st.number_input("Price Per Night (INR)", min_value=500.0, step=500.0, value=5000.0)
            btn_add = st.form_submit_button("Save / Update Room")

        if btn_add:
            try:
                conn = get_connection()
                with conn.cursor() as cursor:
                    # Agar ID exist karti hai toh update karega, nahi toh naya insert karega
                    upsert_query = """
                        INSERT INTO hotel_rooms (room_type_id, room_type_name, available_stock, price_per_night)
                        VALUES (%s, %s, %s, %s)
                        ON DUPLICATE KEY UPDATE 
                            room_type_name = VALUES(room_type_name),
                            available_stock = available_stock + VALUES(available_stock),
                            price_per_night = VALUES(price_per_night);
                    """
                    cursor.execute(upsert_query, (new_room_id, new_room_name, new_room_stock, new_room_price))
                conn.close()
                st.success(f"Room '{new_room_name}' successfully add/update ho gaya!")
                st.rerun()
            except Exception as e:
                st.error(f"Error adding room: {e}")

    # 2. Room Delete karna
    with col_del:
        st.markdown("### 🗑️ Delete Room Type")
        current_rooms = get_room_types()
        if current_rooms:
            with st.form("del_room_form"):
                del_target = st.selectbox(
                    "Select Room to Delete",
                    options=current_rooms,
                    format_func=lambda x: f"ID {x['room_type_id']}: {x['room_type_name']}"
                )
                btn_del = st.form_submit_button("Delete Selected Room")

            if btn_del:
                try:
                    conn = get_connection()
                    with conn.cursor() as cursor:
                        # Pehle check karein bookings to prevent foreign key errors
                        cursor.execute("DELETE FROM room_bookings WHERE room_type_id = %s;", (del_target['room_type_id'],))
                        cursor.execute("DELETE FROM hotel_rooms WHERE room_type_id = %s;", (del_target['room_type_id'],))
                    conn.close()
                    st.success(f"Room ID {del_target['room_type_id']} aur uski linked bookings delete kar di gayi!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error deleting room: {e}")
        else:
            st.info("Delete for no room available.")

# -----------------------------------------------------------------------------
# LIVE DATABASE VERIFICATION SECTION
# -----------------------------------------------------------------------------
st.divider()
st.subheader("🔍 Live Database Inspector (Verify Data in Tables)")

col_btn1, col_btn2 = st.columns(2)
with col_btn1:
    show_acc = st.button("Show Current Guest Accounts")
with col_btn2:
    show_book = st.button("Show Confirmed Bookings & Room Stock")

if show_acc:
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM guest_accounts ORDER BY account_id DESC;")
            res = cursor.fetchall()
            st.write("📋 **guest_accounts Table:**")
            st.dataframe(res, use_container_width=True)
        conn.close()
    except Exception as e:
        st.error(f"Error: {e}")

if show_book:
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM room_bookings ORDER BY booking_id DESC;")
            bookings = cursor.fetchall()
            st.write("📋 **room_bookings Table:**")
            st.dataframe(bookings, use_container_width=True)

            cursor.execute("SELECT * FROM hotel_rooms;")
            rooms = cursor.fetchall()
            st.write("📋 **hotel_rooms Inventory Table (Updated Stock):**")
            st.dataframe(rooms, use_container_width=True)
        conn.close()
    except Exception as e:
        st.error(f"Error: {e}")