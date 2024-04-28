import mysql.connector
from mysql.connector import Error
from flask import Flask, request, jsonify

app = Flask(__name__)

# Configuration for the MySQL connection
db_config = {
    'user':'root',
    'host':'localhost',
    'database':'bootcampit',
    'passwd':'123456'
}

# Connect to the MySQL database
def db_connection():
    conn = None
    try:
        conn = mysql.connector.connect(**db_config)
    except Error as e:
        print(e)
    return conn

def db_connection_close(cursor, conn):
    if cursor:
        cursor.close()
    if conn:
        conn.close()

# Route to create a new student
@app.route('/students', methods=['POST'])
def create_student():
    data = request.get_json()
    first_name = data['firstName']
    last_name = data['lastName']
    enrollment_date = data['enrollmentDate']
    address = data.get('address', None) # Address is optional

    query = """
    INSERT INTO students (FirstName, LastName, EnrollmentDate, Address)
    Values (%s, %s, %s, %s)
    """

    conn = db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(query, (first_name, last_name, enrollment_date, address))
        conn.commit()
        return jsonify(message="Student added successfully"), 201
    except Error as e:
        print(e)
        return jsonify(message="An error occured"), 500
    finally:
        db_connection_close(cursor, conn)

# Route to delete a student
@app.route('/students/<int:student_id>', methods=['DELETE'])
def delete_student(student_id):
    query = "DELETE FROM students WHERE Id = %s"
    conn = db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(query, (student_id,))
        conn.commit()
        if cursor.rowcount > 0:
            return jsonify(message="Student deleted successfully"), 200
        else:
            return jsonify(message="Student not found"), 404
    except Error as e:
        print(e)
        return jsonify(message="An error occured"), 500
    finally:
        db_connection_close(cursor, conn)

# Route to update a student
@app.route('/students/<int:student_id>', methods=['PUT'])
def update_student(student_id):
    data = request.get_json()
    first_name = data.get('firstName')
    last_name = data.get('lastName')
    enrollment_date = data.get('enrollmentDate')
    address = data.get('address')

    conn = db_connection()
    cursor = conn.cursor()

    # We build the update query dynamically based on provided data
    fields = []
    values = []

    if first_name:
        fields.append("FirstName = %s")
        values.append(first_name)
    if last_name:
        fields.append("LastName = %s")
        values.append(last_name)
    if enrollment_date:
        fields.append("EnrollmentDate = %s")
        values.append(enrollment_date)
    if address is not None:  # address can be an empty string to remove the address
        fields.append("Address = %s")
        values.append(address)

    if not fields:
        return jsonify(message="No field to update"), 400

    values.append(student_id)  # append the student id to the values list
    set_clause = ', '.join(fields)
    query = f"UPDATE students SET {set_clause} WHERE Id = %s"

    try:
        cursor.execute(query, values)
        conn.commit()
        if cursor.rowcount > 0:
            return jsonify(message="Student updated successfully"), 200
        else:
            return jsonify(message="Student not found"), 404
    except Error as e:
        print(e)
        return jsonify(message="An error occurred"), 500
    finally:
        db_connection_close(cursor, conn)


if __name__ == '__main__':
    app.run(debug=True)
