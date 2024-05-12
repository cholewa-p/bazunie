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