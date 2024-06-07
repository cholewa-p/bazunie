from flask import Flask, request, redirect, jsonify, render_template, Blueprint
from mysql.connector import Error
from database import db_connection, db_connection_close

subject_route = Blueprint('subject', __name__)
@subject_route.route('/subjects', methods=['GET'])
def get_subjects():
    conn = db_connection()
    cursor = conn.cursor()
    query = """SELECT s.Id, s.Name ,s.Description ,l.FirstName ,l.LastName  from lecturersSubjects ls 
    inner join subjects s on s.Id = ls.SubjectId 
    INNER JOIN lecturers l on l.Id = ls.LecturerId;
    """
    try:
        cursor.execute(query)
        subjects = [
            dict(id=row[0], name=row[1], description=row[2], lecturerFirstName=row[3],lecturerLastName=row[4])
            for row in cursor.fetchall()
        ]
        print(subjects)
        if subjects:
            return render_template('subjects.html', subjects=subjects)
        else:
            return render_template('error.html', error_message="No subjects found")
    except Error as e:
        print(e)

        return render_template('error.html', error_message="An error occurred")
    finally:
        db_connection_close(cursor, conn)
# Route to create a new student
@subject_route.route('/subjects', methods=['POST'])
def create_subject():
    # data = request.get_json()
    name = request.form['name']
    description = request.form['description']
    level = request.form['level']
    price = request.form['price']

    query = """
    INSERT INTO subjects (Name, Description, Price, Level)
    Values (%s, %s, %s, %s)
    """

    conn = db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(query, (name, description, level, price))
        conn.commit()
        return redirect('/subjects')
        # return jsonify(message="Student added successfully"), 201
    except Error as e:
        return render_template('error.html', error_message=e)
        # print(e)
        # return jsonify(message="An error occured"), 500
    finally:
        db_connection_close(cursor, conn)
# Route to delete a student
@subject_route.route('/delete_subject/<int:subject_id>', methods=['POST'])
def delete_subject(subject_id):
    subject_id = str(subject_id)
    # request.form.get['student_id']
    print(subject_id)
    query = "DELETE FROM subjects WHERE Id = %s"
    conn = db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(query, (subject_id,))
        conn.commit()
        if cursor.rowcount > 0:
            return redirect('/subjects')
        else:
            return jsonify(message="subject not found"), 404
    except Error as e:
        print(e)
        return jsonify(message="An error occured"), 500
    finally:
        db_connection_close(cursor, conn)

# Route to update a student
@subject_route.route('/update_subject/<int:subject_id>', methods=['POST'])
def update_subject(subject_id):
    subject_id = str(subject_id)

    name = request.form['name']
    description = request.form['description']
    level = request.form['level']
    price = request.form['price']

    conn = db_connection()
    cursor = conn.cursor()

    # We build the update query dynamically based on provided data
    fields = []
    values = []

    if name:
        fields.append("Name = %s")
        values.append(name)
    if description:
        fields.append("Description = %s")
        values.append(description)
    if price:
        fields.append("Price = %s")
        values.append(price)
    if level:
        fields.append("Level = %s")
        values.append(level)
    if not fields:
        return jsonify(message="No field to update"), 400

    values.append(subject_id)  # append the student id to the values list
    set_clause = ', '.join(fields)
    query = f"UPDATE subjects SET {set_clause} WHERE Id = %s"

    try:
        cursor.execute(query, values)
        conn.commit()
        if cursor.rowcount > 0:
            return redirect('/subjects')
        else:
            return jsonify(message="subject not found"), 404
    except Error as e:
        print(e)
        return jsonify(message="An error occurred"), 500
    finally:
        db_connection_close(cursor, conn)
