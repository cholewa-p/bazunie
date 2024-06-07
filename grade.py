from flask import Flask, request, redirect, jsonify, render_template, Blueprint
from mysql.connector import Error
from database import db_connection, db_connection_close

grade_route = Blueprint('grade', __name__)
@grade_route.route('/grades', methods=['GET'])
def get_grades():
    conn = db_connection()
    cursor = conn.cursor()
    query = "select  c.Name, s.Name, g.Value, g.DateOfReceive, s2.FirstName, s2.LastName,s2.Id from grades g \
                inner join subjects s on g.SubjectId = s.Id \
                inner join courses c on c.Id=s2.CourseId \
                inner join students s2 on s2.Id=g.StudentId"
    try:
        cursor.execute(query)
        grades = [
            dict(courseName=row[0], subject=row[1], value=row[2], date=row[3],firstName=row[4],lastName=row[5],studentId=row[6])
            for row in cursor.fetchall()
        ]
        if grades:
            return render_template('grades.html', grades=grades)
        else:
            return jsonify(message="No grades found"), 404
    except Error as e:
        print(e)
        return jsonify(message=e), 500
    finally:
        db_connection_close(cursor, conn)
@grade_route.route('/grades', methods=['POST'])
def create_grade():
    # data = request.get_json()
    grade = request.form['grade']
    subject_id = request.form['subject']
    student_id = request.form['name']

    query = """
    INSERT INTO grades (Value, DateOfReceive, SubjectId, EnrollmentId)
    Values (%s, now(), %s, %s)
    """
    conn = db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(query, (grade, subject_id, student_id))
        conn.commit()
        return redirect('/grades')
        # return jsonify(message="Student added successfully"), 201
    except Error as e:
        return render_template('error.html', error_message=e)
        # print(e)
        # return jsonify(message="An error occured"), 500
    finally:
        db_connection_close(cursor, conn)
# # Route to delete a student
@grade_route.route('/delete_grade/<int:grade_id>', methods=['POST'])
def delete_grade(grade_id):
    grade_id = str(grade_id)
    request.form.get['grade_id']
    print(grade_id)
    query = "DELETE FROM grades WHERE Id = %s"
    conn = db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(query, (grade_id,))
        conn.commit()
        if cursor.rowcount > 0:
            return redirect('/grades')
        else:
            return jsonify(message="grade not found"), 404
    except Error as e:
        print(e)
        return jsonify(message="An error occured"), 500
    finally:
        db_connection_close(cursor, conn)

# # Route to update a student
@grade_route.route('/update_grade/<int:grade_id>', methods=['POST'])
def update_grade(grade_id):
    grade_id = str(grade_id)
    value = request.form['value']

    conn = db_connection()
    cursor = conn.cursor()

    # We build the update query dynamically based on provided data
    fields = []
    values = []

    if value:
        fields.append("Value = %s")
        values.append(value)
    if not fields:
        return jsonify(message="No field to update"), 400

    values.append(grade_id)  # append the student id to the values list
    set_clause = ', '.join(fields)
    query = f"UPDATE grades SET {set_clause} WHERE Id = %s"

    try:
        cursor.execute(query, values)
        conn.commit()
        if cursor.rowcount > 0:
            return redirect('/grades')
        else:
            return jsonify(message="grade not found"), 404
    except Error as e:
        print(e)
        return jsonify(message="An error occurred"), 500
    finally:
        db_connection_close(cursor, conn)
