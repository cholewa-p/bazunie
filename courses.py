from flask import Flask, request, redirect, jsonify, render_template, Blueprint
from mysql.connector import Error
from database import db_connection, db_connection_close

course_route = Blueprint('course', __name__)
@course_route.route('/courses', methods=['GET'])
def get_courses():
    conn = db_connection()
    cursor = conn.cursor()
    query = "SELECT * FROM courses"
    try:
        cursor.execute(query)
        courses = [
            dict(id=row[0], name=row[1], description=row[2], price=row[3],level=row[4])
            for row in cursor.fetchall()
        ]
        if courses:
            return render_template('courses.html', courses=courses)
        else:
            return jsonify(message="No courses found"), 404
    except Error as e:
        print(e)
        return jsonify(message="An error occurred"), 500
    finally:
        db_connection_close(cursor, conn)
# Route to create a new student
@course_route.route('/courses', methods=['POST'])
def create_course():
    # data = request.get_json()
    name = request.form['name']
    description = request.form['description']
    level = request.form['level']
    price = request.form['price']

    query = """
    INSERT INTO courses (Name, Description, Price, Level)
    Values (%s, %s, %s, %s)
    """

    conn = db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(query, (name, description, level, price))
        conn.commit()
        return redirect('/courses')
        # return jsonify(message="Student added successfully"), 201
    except Error as e:
        return render_template('error.html', error_message=e)
        # print(e)
        # return jsonify(message="An error occured"), 500
    finally:
        db_connection_close(cursor, conn)
# Route to delete a student
@course_route.route('/delete_course/<int:course_id>', methods=['POST'])
def delete_course(course_id):
    course_id = str(course_id)
    # request.form.get['student_id']
    print(course_id)
    query = "DELETE FROM courses WHERE Id = %s"
    conn = db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(query, (course_id,))
        conn.commit()
        if cursor.rowcount > 0:
            return redirect('/courses')
        else:
            return jsonify(message="course not found"), 404
    except Error as e:
        print(e)
        return jsonify(message="An error occured"), 500
    finally:
        db_connection_close(cursor, conn)

# Route to update a student
@course_route.route('/update_course/<int:course_id>', methods=['POST'])
def update_course(course_id):
    course_id = str(course_id)

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

    values.append(course_id)  # append the student id to the values list
    set_clause = ', '.join(fields)
    query = f"UPDATE courses SET {set_clause} WHERE Id = %s"

    try:
        cursor.execute(query, values)
        conn.commit()
        if cursor.rowcount > 0:
            return redirect('/courses')
        else:
            return jsonify(message="course not found"), 404
    except Error as e:
        print(e)
        return jsonify(message="An error occurred"), 500
    finally:
        db_connection_close(cursor, conn)
