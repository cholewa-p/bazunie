from flask import Flask, request, redirect, jsonify, render_template, Blueprint,session
from mysql.connector import Error
from datetime import datetime
from database import db_connection, db_connection_close
# from main import app as grade_app, grade_route
grade_route = Blueprint('grade', __name__)
@grade_route.route('/grades', methods=['GET'])
def get_grades():
    conn = db_connection()
    id=session['student_id']
    user=session['username']
    cursor = conn.cursor()
    if user=='admin':
        query = "select g.Value, s2.Name , g.DateOfReceive, g.StudentId, g.Id from grades g inner join students s on g.StudentId =s.Id inner join subjects s2 on g.SubjectId =s2.Id;"
    else:
        query = """ select g.Value, s2.Name , g.DateOfReceive, g.StudentId from grades g 
            inner join students s on g.StudentId =s.Id 
            inner join subjects s2 on g.SubjectId =s2.Id
            WHERE s.Id = %s; """%id
    # query = """select  c.Name, s.Name, g.Value, g.DateOfReceive, s2.FirstName, s2.LastName,s2.Id from grades g \
    #             inner join subjects s on g.SubjectId = s.Id 
    #             inner join courses c on c.Id=s2.CourseId 
    #             inner join students s2 on s2.Id=g.StudentId"""
    try:
        cursor.execute(query)
        grades = [
            dict(value=row[0], subject=row[1], date=row[2],student_id=row[3],id=row[4])
            for row in cursor.fetchall()
        ]
        print(grades)
        if grades:
            return render_template('grades.html', grades=grades,user=user)
        else:
            return render_template('error.html', error_message="No grades found")
    except Error as e:
        print(e)
        return jsonify(message=e), 500
    finally:
        db_connection_close(cursor, conn)
@grade_route.route('/grades', methods=['POST'])
def create_grade():
    grade = request.form['grade']
    subject_id = request.form['subjectId']
    student_id = request.form['studentId']

    query = """
    INSERT INTO grades (Value, DateOfReceive, SubjectId, StudentId)
    Values (%s, %s, %s, %s)
    """
    conn = db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(query, (grade, datetime.now() ,subject_id, student_id))
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
    # request.form.get['grade_id']
    print(f"gradeID:{grade_id}")
    query = "DELETE FROM grades WHERE Id = %s"
    conn = db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(query, (grade_id,))
        conn.commit()
        if cursor.rowcount > 0:
            return redirect('/grades')
        else:
            return render_template('error.html', error_message="No grades found")
    except Error as e:
        print(e)
        return render_template('error.html', error_message=e)
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
            return render_template('error.html', error_message="No grades found")
    except Error as e:
        print(e)
        return render_template('error.html', error_message=e)
    finally:
        db_connection_close(cursor, conn)
