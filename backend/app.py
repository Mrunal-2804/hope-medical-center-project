import os
from dotenv import load_dotenv
import mysql.connector
from flask import Flask, jsonify, request
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash

load_dotenv()

app = Flask(__name__)
CORS(app)

# Database Connection Helper Function
def get_db_connection():
    # Connects to the host server without assuming the database exists yet
    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        port=3306
    )

# Bootstrap function to ensure database shell and tables exist
def initialize_database():
    try:
        # 1. Connect to the global MySQL server
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 2. Create the empty database shell if missing
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {os.getenv('DB_NAME', 'medical_db')};")
        
        # 3. Target the newly created database explicitly
        cursor.execute(f"USE {os.getenv('DB_NAME', 'medical_db')};")
        
        # 4. Generate the users table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                full_name VARCHAR(255) NOT NULL,
                email VARCHAR(255) NOT NULL UNIQUE,
                password_hash VARCHAR(255) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        
        # 5. Generate the appointments table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS appointments (
                id INT AUTO_INCREMENT PRIMARY KEY,
                full_name VARCHAR(255) NOT NULL,
                email VARCHAR(255) NOT NULL,
                phone VARCHAR(50) NOT NULL,
                department VARCHAR(255) NOT NULL,
                date_time DATETIME NOT NULL,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        
        conn.commit()
        cursor.close()
        conn.close()
        print("🎉 Cloud Database and Tables successfully verified/created!")
    except Exception as e:
        print(f"⚠️ Initialization Error: {e}")

# Helper function to grab a functional cursor pinned to your database
def get_active_cursor(dictionary=False):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=dictionary)
    cursor.execute(f"USE {os.getenv('DB_NAME', 'medical_db')};")
    return conn, cursor

# Securely register and hash a new user in the database
def signup_user(full_name, email, plain_text_password):
    conn, cursor = get_active_cursor()
    hashed_password = generate_password_hash(plain_text_password)
    insert_query = "INSERT INTO users (full_name, email, password_hash) VALUES (%s, %s, %s)"
    cursor.execute(insert_query, (full_name, email, hashed_password))
    conn.commit()
    cursor.close()
    conn.close()

# Check a user's credentials on login
def authenticate_user(email, plain_text_password):
    conn, cursor = get_active_cursor(dictionary=True)
    cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
    user = cursor.fetchone()
    cursor.close()
    conn.close()
    if user and check_password_hash(user['password_hash'], plain_text_password):
        return user
    return None

# 1. This endpoint tests the connection (runs on page load)
@app.route('/api/status', methods=['GET'])
def get_status():
    try:
        conn, cursor = get_active_cursor()
        cursor.close()
        conn.close()
        return jsonify({
            "status": "success",
            "message": "Hello from the Python Backend! Database connection successful."
        })
    except mysql.connector.Error as err:
        return jsonify({
            "status": "error",
            "message": f"Database connection failed: {err}"
        }), 500

# 2. This endpoint receives the form data when a user books an appointment
@app.route('/api/book-appointment', methods=['POST'])
def book_appointment():
    try:
        data = request.json
        if not data:
            return jsonify({"status": "error", "message": "No data received."}), 400

        full_name   = data.get('fullName')
        email       = data.get('email')
        phone       = data.get('phone')
        department  = data.get('department')
        date_time   = data.get('dateTime')
        notes       = data.get('notes', 'None Provided')

        print("\n--- NEW APPOINTMENT RECEIVED ---")
        print(f"Patient: {full_name}\nEmail: {email}\nPhone: {phone}")
        print("--------------------------------\n")

        if date_time and 'T' in date_time:
            date_time = date_time.replace('T', ' ')
            if len(date_time) == 16:
                date_time += ':00'

        conn, cursor = get_active_cursor()
        insert_query = (
            "INSERT INTO appointments "
            "(full_name, email, phone, department, date_time, notes) "
            "VALUES (%s, %s, %s, %s, %s, %s)"
        )
        cursor.execute(insert_query, (full_name, email, phone, department, date_time, notes))
        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({
            "status": "success",
            "message": "Appointment saved to the database successfully."
        }), 201
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/signup', methods=['POST'])
def signup():
    try:
        data = request.json
        if not data:
            return jsonify({"status": "error", "message": "No signup data received."}), 400

        full_name = data.get('name')
        email = data.get('email')
        password = data.get('password')

        if not full_name or not email or not password:
            return jsonify({"status": "error", "message": "Name, email, and password are required."}), 400
            
        conn, cursor = get_active_cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        existing = cursor.fetchone()
        cursor.close()
        conn.close()

        if existing:
            if check_password_hash(existing['password_hash'], password):
                return jsonify({"status": "success", "message": "Existing account detected — logged in."}), 200
            else:
                return jsonify({"status": "error", "message": "This email is already registered."}), 400

        signup_user(full_name, email, password)
        return jsonify({"status": "success", "message": "Signup successful. You are now logged in."}), 201
    except mysql.connector.Error as err:
        return jsonify({"status": "error", "message": f"Database error: {err}"}), 500
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/login', methods=['POST'])
def login():
    try:
        data = request.json
        if not data:
            return jsonify({"status": "error", "message": "No login data received."}), 400

        email = data.get('email')
        password = data.get('password')
        if not email or not password:
            return jsonify({"status": "error", "message": "Email and password are required."}), 400

        user = authenticate_user(email, password)
        if user:
            return jsonify({"status": "success", "message": "Login successful."})
        return jsonify({"status": "error", "message": "Invalid email or password."}), 401
    except mysql.connector.Error as err:
        return jsonify({"status": "error", "message": f"Database error: {err}"}), 500
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# Run initialization once upon starting the server script
initialize_database()

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)