import mysql.connector
from flask import Flask, jsonify, request
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
# CORS ensures your local index.html frontend is allowed to speak to this backend
CORS(app)

# Database Connection Helper Function
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",          # Change if your MySQL username is different
        password="ADMIN",     # PUT YOUR ACTUAL MYSQL PASSWORD HERE
        database="medical_db",
        port=3306
    )

# Ensure the appointments table exists before inserting records
def ensure_appointments_table():
    conn = get_db_connection()
    cursor = conn.cursor()
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

# Ensure the users table exists before registering or authenticating records
def ensure_users_table():
    conn = get_db_connection()
    cursor = conn.cursor()
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
    conn.commit()
    cursor.close()
    conn.close()

# Securely register and hash a new user in the database
def signup_user(full_name, email, plain_text_password):
    ensure_users_table()  # Make sure table exists first
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Hash the password for safety before saving
    hashed_password = generate_password_hash(plain_text_password)
    
    insert_query = "INSERT INTO users (full_name, email, password_hash) VALUES (%s, %s, %s)"
    cursor.execute(insert_query, (full_name, email, hashed_password))
    conn.commit()
    
    cursor.close()
    conn.close()

# Check a user's credentials on login
def authenticate_user(email, plain_text_password):
    ensure_users_table()  # Make sure table exists first
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
    user = cursor.fetchone()
    
    cursor.close()
    conn.close()
    
    # Check if user exists and password hash matches
    if user and check_password_hash(user['password_hash'], plain_text_password):
        return user
    return None


# 1. This endpoint tests the connection (runs on page load)
@app.route('/api/status', methods=['GET'])
def get_status():
    try:
        conn = get_db_connection()
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
        # Get the JSON data sent from code.js
        data = request.json
        
        # If no data came through, return an error
        if not data:
            return jsonify({
                "status": "error",
                "message": "No data received."
            }), 400

        # Extract the fields exactly as sent by your frontend
        full_name   = data.get('fullName')
        email       = data.get('email')
        phone       = data.get('phone')
        department  = data.get('department')
        date_time   = data.get('dateTime')
        notes       = data.get('notes', 'None Provided')

        # For now, we print it to your terminal screen to prove it works!
        print("\n--- NEW APPOINTMENT RECEIVED ---")
        print(f"Patient: {full_name}")
        print(f"Email: {email}")
        print(f"Phone: {phone}")
        print(f"Department: {department}")
        print(f"Time: {date_time}")
        print(f"Notes: {notes}")
        print("--------------------------------\n")

        # Convert the date/time into MySQL-friendly format if needed
        if date_time and 'T' in date_time:
            date_time = date_time.replace('T', ' ')
            if len(date_time) == 16:
                date_time += ':00'

        # Ensure the appointments table exists
        ensure_appointments_table()

        # Insert the appointment into the MySQL database
        conn = get_db_connection()
        cursor = conn.cursor()
        insert_query = (
            "INSERT INTO appointments "
            "(full_name, email, phone, department, date_time, notes) "
            "VALUES (%s, %s, %s, %s, %s, %s)"
        )
        cursor.execute(insert_query, (
            full_name,
            email,
            phone,
            department,
            date_time,
            notes
        ))
        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({
            "status": "success",
            "message": "Appointment saved to the database successfully."
        }), 201

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


@app.route('/api/signup', methods=['POST'])
def signup():
    try:
        data = request.json
        if not data:
            return jsonify({
                "status": "error",
                "message": "No signup data received."
            }), 400

        full_name = data.get('name')
        email = data.get('email')
        password = data.get('password')

        if not full_name or not email or not password:
            return jsonify({
                "status": "error",
                "message": "Name, email, and password are required."
            }), 400
            
        # If a user already exists with this email, check password to optionally auto-login
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        existing = cursor.fetchone()
        cursor.close()
        conn.close()

        if existing:
            # If password matches existing account, treat as successful login
            if check_password_hash(existing['password_hash'], password):
                return jsonify({
                    "status": "success",
                    "message": "Existing account detected — logged in."
                }), 200
            else:
                return jsonify({
                    "status": "error",
                    "message": "This email is already registered. Please log in or reset your password."
                }), 400

        # Otherwise create a new user
        signup_user(full_name, email, password)
        return jsonify({
            "status": "success",
            "message": "Signup successful. You are now logged in."
        }), 201
    except mysql.connector.Error as err:
        return jsonify({
            "status": "error",
            "message": f"Database error: {err}"
        }), 500
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


@app.route('/api/login', methods=['POST'])
def login():
    try:
        data = request.json
        if not data:
            return jsonify({
                "status": "error",
                "message": "No login data received."
            }), 400

        email = data.get('email')
        password = data.get('password')
        if not email or not password:
            return jsonify({
                "status": "error",
                "message": "Email and password are required."
            }), 400

        user = authenticate_user(email, password)
        if user:
            return jsonify({
                "status": "success",
                "message": "Login successful."
            })
        return jsonify({
            "status": "error",
            "message": "Invalid email or password."
        }), 401
    except mysql.connector.Error as err:
        return jsonify({
            "status": "error",
            "message": f"Database error: {err}"
        }), 500
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500
        


if __name__ == '__main__':
    # Runs the server on http://127.0.0.1:5000
    app.run(debug=True, port=5000)