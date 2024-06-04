from flask import Flask, request, redirect, jsonify, render_template, Blueprint
from mysql.connector import Error
from database import db_connection, db_connection_close
enrollment_route = Blueprint('enrollment', __name__)
@enrollment_route.route('/enrollments', methods=['GET'])
def get_enrollments():
    conn = db_connection()
    cursor = conn.cursor()
    query = "SELECT * FROM enrollments"
    try:
        cursor.execute(query)
        enrollments = [
            dict(id=row[0], courseId=row[1], studentId=row[2], paymentId=row[3],finalScore=row[4], createdOn=str(row[5]))
            for row in cursor.fetchall()
        ]
        if enrollments:
            return render_template('enrollments.html', enrollments=enrollments)
    except Error as e:
        print(e)
        return render_template('error.html', error_message=e)
            