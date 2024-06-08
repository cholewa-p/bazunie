from flask import Flask, render_template, request, redirect, url_for, session, flash, Blueprint
from flask_bcrypt import generate_password_hash, Bcrypt, check_password_hash
from sqlite3 import IntegrityError
from datetime import datetime

from student import student_route
from lecturer import lecturer_route
from courses import course_route
from grade import grade_route
from subjects import subject_route
from payments import payment_route

from database import db_connection, db_connection_close
app = Flask(__name__)
app.secret_key = 'your_secret_key'
bcrypt = Bcrypt(app)

app.register_blueprint(student_route)
app.register_blueprint(lecturer_route)
app.register_blueprint(course_route)
app.register_blueprint(grade_route)
app.register_blueprint(subject_route)
app.register_blueprint(payment_route)

#Route to main page
@app.route('/')
def index():
    if 'username' in session:
        return render_template('./index.html')
    else:
        return render_template('./start.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT Id, Password FROM students WHERE Login = %s", (username,))
        student = cursor.fetchone()
        db_connection_close(cursor, conn)
        print(student)
        if student and check_password_hash(student[1], password):
            session['student_id'] = student[0]
            session['username'] = username
            print("login successful")
            flash('Login successful!', 'success')
            return render_template('index.html')
        # redirect(url_for('index'))
        else:
            flash('Login failed. Check your username and password.', 'danger')
    
    return render_template('start.html')


@app.route('/logout')
def logout():
    session.pop('student_id', None)
    session.pop('username', None)
    flash('You have been logged out.', 'success')
    # return redirect(url_for('start'))
    return render_template('./start.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        firstname = request.form['firstname']
        lastname = request.form['lastname']
        username = request.form['username']
        password = request.form['password']
        hashed_password = generate_password_hash(password).decode('utf-8')
        enrollmentdate=datetime.now()
        conn = db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO students (FirstName, LastName, EnrollmentDate, Login, Password ) VALUES (%s, %s, %s, %s, %s)", (firstname, lastname,enrollmentdate, username, hashed_password ))
            conn.commit()
            flash('Registration successful!', 'success')
            return redirect(url_for('login'))
        except IntegrityError:
            flash('Username already exists. Please choose a different one.', 'danger')
        finally:
            db_connection_close(cursor, conn)
    
    return render_template('register.html')

if __name__ == '__main__':
    app.run(debug=True)