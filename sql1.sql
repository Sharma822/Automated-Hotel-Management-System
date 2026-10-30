DROP DATABASE IF EXISTS hotel_management_db;
CREATE DATABASE hotel_management_db;
USE hotel_management_db;

CREATE TABLE guest_accounts (
    account_id INT PRIMARY KEY,
    guest_name VARCHAR(100) NOT NULL,
    account_balance DECIMAL(10, 2) NOT NULL
);

CREATE TABLE hotel_inventory (
    item_id INT AUTO_INCREMENT PRIMARY KEY,
    item_name VARCHAR(100) NOT NULL,
    current_stock INT NOT NULL,
    reorder_level INT NOT NULL
);

CREATE TABLE hotel_employees (
    emp_id INT AUTO_INCREMENT PRIMARY KEY,
    emp_name VARCHAR(100) NOT NULL,
    job_role VARCHAR(50) NOT NULL,
    basic_salary DECIMAL(10, 2) NOT NULL
);

CREATE TABLE hotel_rooms (
    room_type_id INT PRIMARY KEY,
    room_type_name VARCHAR(50) NOT NULL,
    available_stock INT NOT NULL,
    price_per_night DECIMAL(10, 2) NOT NULL
);

CREATE TABLE room_bookings (
    booking_id INT AUTO_INCREMENT PRIMARY KEY,
    guest_name VARCHAR(100) NOT NULL,
    room_type_id INT NOT NULL,
    rooms_booked INT NOT NULL,
    total_amount DECIMAL(10, 2) DEFAULT 0.00,
    booking_status VARCHAR(20) DEFAULT 'CONFIRMED',
    booking_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (room_type_id) REFERENCES hotel_rooms(room_type_id)
);

INSERT INTO guest_accounts (account_id, guest_name, account_balance) VALUES
(201, 'Aakash Sharma', 1200.00);

INSERT INTO hotel_inventory (item_name, current_stock, reorder_level) VALUES
('Toiletries Kit', 15, 25),
('Bath Towels', 8, 20),
('Bed Linens', 40, 30),
('Mineral Water Bottles', 12, 50);

INSERT INTO hotel_employees (emp_name, job_role, basic_salary) VALUES
('Anita Sharma', 'Front Desk', 25000.00),
('Vikas Singh', 'Manager', 55000.00),
('Sunil Yadav', 'Housekeeping', 18000.00);

INSERT INTO hotel_rooms (room_type_id, room_type_name, available_stock, price_per_night) VALUES
(1, 'Deluxe Room', 10, 3500.00),
(2, 'Super Deluxe Suite', 5, 7000.00);

DROP PROCEDURE IF EXISTS sp_create_guest_account;
DELIMITER $$
CREATE PROCEDURE sp_create_guest_account (
    IN p_account_id INT,
    IN p_guest_name VARCHAR(100),
    IN p_balance DECIMAL(10, 2),
    OUT p_status_msg VARCHAR(255)
)
BEGIN
    DECLARE min_required DECIMAL(10, 2) DEFAULT 1000.00;
    DECLARE v_exists INT DEFAULT 0;
    
    SELECT COUNT(*) INTO v_exists FROM guest_accounts WHERE account_id = p_account_id;
    
    IF v_exists > 0 THEN
        SET p_status_msg = CONCAT('FAILED: Account ID ', p_account_id, ' already exists.');
    ELSEIF p_balance < min_required THEN
        SET p_status_msg = CONCAT('FAILED: Minimum balance required is INR ', min_required);
    ELSE
        INSERT INTO guest_accounts (account_id, guest_name, account_balance)
        VALUES (p_account_id, p_guest_name, p_balance);
        SET p_status_msg = 'SUCCESS: Account created successfully.';
    END IF;
END$$
DELIMITER ;

DROP PROCEDURE IF EXISTS sp_generate_low_stock_report;
DELIMITER $$
CREATE PROCEDURE sp_generate_low_stock_report ()
BEGIN
    DECLARE done INT DEFAULT FALSE;
    DECLARE v_id INT;
    DECLARE v_name VARCHAR(100);
    DECLARE v_stock INT;
    DECLARE v_reorder INT;

    DECLARE cur_low_stock CURSOR FOR 
        SELECT item_id, item_name, current_stock, reorder_level 
        FROM hotel_inventory 
        WHERE current_stock < reorder_level;
        
    DECLARE CONTINUE HANDLER FOR NOT FOUND SET done = TRUE;

    CREATE TEMPORARY TABLE IF NOT EXISTS temp_low_stock_report (
        item_id INT,
        item_name VARCHAR(100),
        current_stock INT,
        reorder_level INT
    );
    TRUNCATE TABLE temp_low_stock_report;

    OPEN cur_low_stock;
    read_loop: LOOP
        FETCH cur_low_stock INTO v_id, v_name, v_stock, v_reorder;
        IF done THEN
            LEAVE read_loop;
        END IF;
        INSERT INTO temp_low_stock_report VALUES (v_id, v_name, v_stock, v_reorder);
    END LOOP;
    CLOSE cur_low_stock;

    SELECT * FROM temp_low_stock_report;
END$$
DELIMITER ;

DROP FUNCTION IF EXISTS fn_calc_emp_bonus;
DELIMITER $$
CREATE FUNCTION fn_calc_emp_bonus(p_salary DECIMAL(10, 2))
RETURNS DECIMAL(10, 2)
DETERMINISTIC
BEGIN
    DECLARE v_bonus DECIMAL(10, 2);
    
    IF p_salary < 20000.00 THEN
        SET v_bonus = p_salary * 0.15;
    ELSEIF p_salary <= 40000.00 THEN
        SET v_bonus = p_salary * 0.12;
    ELSE
        SET v_bonus = p_salary * 0.10;
    END IF;
    
    RETURN ROUND(v_bonus, 2);
END$$
DELIMITER ;

DROP PROCEDURE IF EXISTS sp_process_room_booking;
DELIMITER $$
CREATE PROCEDURE sp_process_room_booking (
    IN p_guest_name VARCHAR(100),
    IN p_room_type_id INT,
    IN p_qty INT,
    OUT p_booking_id INT,
    OUT p_msg VARCHAR(255)
)
BEGIN
    DECLARE v_current_stock INT DEFAULT 0;
    DECLARE v_room_price DECIMAL(10, 2) DEFAULT 0.00;
    
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        SET p_booking_id = 0;
        SET p_msg = 'FAILED: Database transaction failed and rolled back.';
    END;

    START TRANSACTION;

    SELECT available_stock, price_per_night 
    INTO v_current_stock, v_room_price 
    FROM hotel_rooms 
    WHERE room_type_id = p_room_type_id 
    FOR UPDATE;

    IF v_current_stock IS NULL THEN
        ROLLBACK;
        SET p_booking_id = 0;
        SET p_msg = 'FAILED: Selected room type does not exist.';
    ELSEIF v_current_stock < p_qty THEN
        ROLLBACK;
        SET p_booking_id = 0;
        SET p_msg = CONCAT('FAILED: Insufficient rooms. Only ', v_current_stock, ' available.');
    ELSE
        UPDATE hotel_rooms 
        SET available_stock = available_stock - p_qty 
        WHERE room_type_id = p_room_type_id;

        INSERT INTO room_bookings (guest_name, room_type_id, rooms_booked, total_amount, booking_status)
        VALUES (p_guest_name, p_room_type_id, p_qty, (v_room_price * p_qty), 'CONFIRMED');

        SET p_booking_id = LAST_INSERT_ID();
        SET p_msg = 'SUCCESS: Room booked successfully.';
        
        COMMIT;
    END IF;
END$$
DELIMITER ;

SELECT * FROM guest_accounts;
SELECT * FROM hotel_inventory;
SELECT * FROM hotel_employees;
SELECT * FROM hotel_rooms;
SELECT * FROM room_bookings;