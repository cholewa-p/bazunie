from flask import Flask, request, redirect, jsonify, render_template, Blueprint, session
from mysql.connector import Error
from database import db_connection, db_connection_close
# from main import app as subject_app, subject_route
subject_route = Blueprint('subject', __name__)
@subject_route.route('/subjects', methods=['GET'])
def get_subjects():
    id=session['student_id']
    conn = db_connection()
    cursor = conn.cursor()
    user=session['username']
    if user=='admin':
        query = "select c.Name,s2.Name, s2.Description, s2.Id,l.FirstName ,l.LastName  from coursesSubjects cs inner join courses c on c.Id = cs.CourseId inner join students s on c.Id = s.CourseId inner join subjects s2 on s2.Id = cs.SubjectId inner join lecturersSubjects ls on ls.SubjectId = s.Id inner join lecturers l on ls.LecturerId =l.Id"
    else:
        query = "select c.Name,s2.Name, s2.Description, s2.Id,l.FirstName ,l.LastName from coursesSubjects cs inner join courses c on c.Id = cs.CourseId inner join students s on c.Id = s.CourseId inner join subjects s2 on s2.Id = cs.SubjectId inner join lecturersSubjects ls on ls.SubjectId = s.Id inner join lecturers l on ls.LecturerId =l.Id WHERE s.Id =%s;"%id
    # query = """SELECT s.Id, s.Name ,s.Description ,l.FirstName ,l.LastName  from lecturersSubjects ls 
    # inner join subjects s on s.Id = ls.SubjectId 
    # INNER JOIN lecturers l on l.Id = ls.LecturerId;
    # """
    try:
        cursor.execute(query)
        subjects = [
            dict(courseName=row[0], subjectName=row[1],description=row[2],subjectId=row[3],firstName=row[4],lastName=row[5])
            for row in cursor.fetchall()
        ]
        print(subjects)
        if subjects:
            return render_template('subjects.html', subjects=subjects,user=user)
        else:
            return render_template('error.html', error_message="No subjects found")
    except Error as e:
        print(e)

        return render_template('error.html', error_message="An error occurred")
    finally:
        db_connection_close(cursor, conn)
# Route to create a new subject
@subject_route.route('/subjects', methods=['POST'])
def create_subject():
    # data = request.get_json()
    name = request.form['name']
    description = request.form['description']

    query = """
    INSERT INTO subjects (Name, Description)
    Values (%s, %s)
    """

    conn = db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(query, (name, description))
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
