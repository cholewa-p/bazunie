from flask import Flask, request, redirect, jsonify, render_template, Blueprint, session
from mysql.connector import Error
from datetime import datetime
from database import db_connection, db_connection_close
# from main import session
# Route to get all students
student_route = Blueprint('student', __name__)
@student_route.route('/students', methods=['GET'])
def get_students():
    conn = db_connection()
    cursor = conn.cursor()
    id=session['student_id']
    user=session['username']
    query2=None
    notadded=[]
    if user=='admin':
        query = "SELECT s.Id,s.FirstName,s.LastName,s.EnrollmentDate,s.Address,courses.Name FROM students s inner join courses on s.CourseId = courses.Id"
        query2="SELECT s.Id, s.FirstName, s.LastName FROM students s where s.CourseId  IS NULL and not s.Login = 'admin';"
    else:
        query = "SELECT s.Id,s.FirstName,s.LastName,s.EnrollmentDate,s.Address,courses.Name FROM students s inner join courses on s.CourseId = courses.Id where s.Id=%s" %id
    try:
        if query2:
            cursor.execute(query2)
            notadded = [
                dict(id=row[0], firstName=row[1], lastName=row[2])
                for row in cursor.fetchall()
            ]
        cursor.execute(query)
        students = [
            dict(id=row[0], firstName=row[1], lastName=row[2], enrollmentDate=str(row[3]), address=row[4],course=row[5])
            for row in cursor.fetchall()
        ]
        if students:
            return render_template('students.html', students=students,user=user,notadded=notadded)
        else:
            return jsonify(message="No students found"), 404
    except Error as e:
        print(e)
        return render_template('error.html', error_message=e)
    finally:
        db_connection_close(cursor, conn)

# Route to get a single student by ID
@student_route.route('/students/<int:student_id>', methods=['GET'])
def get_student(student_id):
    conn = db_connection()
    cursor = conn.cursor()
    query = "SELECT * FROM students WHERE Id = %s"
    try:
        cursor.execute(query, (student_id,))
        row = cursor.fetchone()
        if row:
            student = dict(id=row[0], firstName=row[1], lastName=row[2], enrollmentDate=str(row[3]), address=row[4])
            return jsonify(student), 200
        else:
            return jsonify(message="Student not found"), 404
    except Error as e:
        print(e)
        return render_template('error.html', error_message=e)
    finally:
        db_connection_close(cursor, conn)

# Route to create a new student
@student_route.route('/students', methods=['POST'])
def create_student():
    # data = request.get_json()
    first_name = request.form['firstName']
    last_name = request.form['lastName']
    enrollment_date = datetime.now()
    # request.form['enrollmentDate']
    address = request.form['address']

    query = """
    INSERT INTO students (FirstName, LastName, EnrollmentDate, Address, Login, Password)
    Values (%s, %s, %s, %s, 'test', 'test')
    """

    conn = db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(query, (first_name, last_name, enrollment_date, address))
        conn.commit()
        return redirect('/students')
    except Error as e:
        print(e)
        return jsonify(message="An error occured"), 500
    finally:
        db_connection_close(cursor, conn)

# Route to delete a student
@student_route.route('/delete_student/<int:student_id>', methods=['POST'])
def delete_student(student_id):
    student_id = str(student_id)
    # request.form.get['student_id']
    print(student_id)
    query = "DELETE FROM students WHERE Id = %s"
    conn = db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(query, (student_id,))
        conn.commit()
        if cursor.rowcount > 0:
            return redirect('/students')
        else:
            return render_template('error.html', error_message="Student not found")
    except Error as e:
        print(e)
        return render_template('error.html', error_message=e)
    finally:
        db_connection_close(cursor, conn)

# Route to update a student
@student_route.route('/update_student/<int:student_id>', methods=['POST'])
def update_student(student_id):
    student_id = str(student_id)
    # data = request.get_json()
    first_name = request.form['firstName']
    last_name = request.form['lastName']
    address = request.form['address']

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
            return redirect('/students')
        else:
            return jsonify(message="Student not found"), 404
    except Error as e:
        print(e)
        return jsonify(message="An error occurred"), 500
    finally:
        db_connection_close(cursor, conn)
