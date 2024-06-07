from flask import Flask, request, redirect, jsonify, render_template, Blueprint
from mysql.connector import Error
from database import db_connection, db_connection_close

lecturer_route = Blueprint('lecturer', __name__)
@lecturer_route.route('/lecturers', methods=['GET'])
def get_lecturers():
    conn = db_connection()
    cursor = conn.cursor()
    query = "SELECT * FROM lecturers"
    try:
        cursor.execute(query)
        lecturers = [
            dict(id=row[0], firstName=row[1], lastName=row[2], title=row[3])
            for row in cursor.fetchall()
        ]
        if lecturers:
            return render_template('lecturers.html', lecturers=lecturers)
        else:
            return jsonify(message="No lecturers found"), 404
    except Error as e:
        print(e)
        return jsonify(message="An error occurred"), 500
    finally:
        db_connection_close(cursor, conn)
# Route to create a new student
@lecturer_route.route('/lecturers', methods=['POST'])
def create_lecturer():
    # data = request.get_json()
    first_name = request.form['firstName']
    last_name = request.form['lastName']
    title = request.form['title']

    query = """
    INSERT INTO lecturers (FirstName, LastName, Title)
    Values (%s, %s, %s)
    """
    conn = db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(query, (first_name, last_name, title))
        conn.commit()
        return redirect('/lecturers')
        # return jsonify(message="Student added successfully"), 201
    except Error as e:
        return render_template('error.html', error_message=e)
        # print(e)
        # return jsonify(message="An error occured"), 500
    finally:
        db_connection_close(cursor, conn)
# Route to delete a student
@lecturer_route.route('/delete_lecturer/<int:lecturer_id>', methods=['POST'])
def delete_lecturer(lecturer_id):
    lecturer_id = str(lecturer_id)
    # request.form.get['student_id']
    print(lecturer_id)
    query = "DELETE FROM lecturers WHERE Id = %s"
    conn = db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(query, (lecturer_id,))
        conn.commit()
        if cursor.rowcount > 0:
            return redirect('/lecturers')
        else:
            return jsonify(message="Lecturer not found"), 404
    except Error as e:
        print(e)
        return jsonify(message="An error occured"), 500
    finally:
        db_connection_close(cursor, conn)

# Route to update a student
@lecturer_route.route('/update_lecturer/<int:lecturer_id>', methods=['POST'])
def update_lecturer(lecturer_id):
    lecturer_id = str(lecturer_id)
    # data = request.get_json()
    first_name = request.form['firstName']
    last_name = request.form['lastName']
    title = request.form['title']

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
    if title:
        fields.append("Title = %s")
        values.append(title)


    if not fields:
        return jsonify(message="No field to update"), 400

    values.append(lecturer_id)  # append the student id to the values list
    set_clause = ', '.join(fields)
    query = f"UPDATE lecturers SET {set_clause} WHERE Id = %s"

    try:
        cursor.execute(query, values)
        conn.commit()
        if cursor.rowcount > 0:
            return redirect('/lecturers')
        else:
            return jsonify(message="Lecturer not found"), 404
    except Error as e:
        print(e)
        return jsonify(message="An error occurred"), 500
    finally:
        db_connection_close(cursor, conn)
