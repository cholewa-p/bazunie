from flask import Flask, request, jsonify
import mysql.connector
from mysql.connector import Error

app = Flask(__name__)

# Database configuration
config = {
    'user': 'root',
    'password': '1234',
    'host': 'localhost',
    'database': 'baza_bootcamp',
    'port': '33061',
    'raise_on_warnings': True
}

def create_connection():
    """Create a database connection"""
    conn = None
    try:
        conn = mysql.connector.connect(**config)
        if conn.is_connected():
            print('Connected to MySQL database')
    except Error as e:
        print(e)
        print("failed")
    return conn

def execute_query(query, args=()):
    """Execute a single query"""
    conn = create_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(query, args)
        conn.commit()
        print("Query successful")
    except Error as e:
        print(f"Error: {e}")
    finally:
        cursor.close()
        conn.close()

def query_db(query, args=(), one=False):
    """Query the database and return the results"""
    conn = create_connection()
    cursor = conn.cursor()
    result = None
    try:
        cursor.execute(query, args)
        result = cursor.fetchall()
        return (result[0] if result else None) if one else result
    except Error as e:
        print(f"Error: {e}")
        return None
    finally:
        cursor.close()
        conn.close()

@app.route('/add_student', methods=['POST'])
def add_student():
    data = request.get_json()
    query = """
    INSERT INTO Students (FirstName, LastName, EnrollmentDate, Address)
    VALUES (%s, %s, %s, %s)
    """
    args = (data['FirstName'], data['LastName'], data['EnrollmentDate'], data['Address'])
    try:
        execute_query(query, args)
        return jsonify({'message': 'Student added successfully'}), 201
    except:
        return jsonify({'message': 'Error adding student'}), 500
@app.route('/students', methods=['GET'])
def get_students():
    query = "SELECT * FROM Students;"
    result = query_db(query)
    return jsonify(result), 200
if __name__ == '__main__':
    app.run()