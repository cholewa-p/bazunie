from flask import Flask, request, redirect, jsonify, render_template, Blueprint, session
from mysql.connector import Error
from datetime import datetime
from database import db_connection, db_connection_close
# from main import app
# from main import app as payment_app, payment_route
payment_route = Blueprint('payment', __name__)
@payment_route.route('/payments', methods=['GET'])
def get_payments():
    conn = db_connection()
    cursor = conn.cursor()
    id=session['student_id']
    user=session['username']
    if user=='admin':
        query = "SELECT p.Amount,p.DateOfPayment,p.Id, s.Id from studentsPayments sp inner join students s on s.Id =sp.StudentId inner join payments p on p.Id = sp.PaymentId"
    else:
    # query = "SELECT * FROM students where Id=%s" %id
        query = """SELECT p.Amount,p.DateOfPayment,p.Id, s.Id  from studentsPayments sp 
            inner join students s on s.Id = sp.StudentId 
            inner join payments p on p.Id = sp.PaymentId
            where s.Id=%s; """ %id
   
    try:
        cursor.execute(query)
        payments = [
            dict(amount=row[0], dateOfPayment=row[1],paymentId=row[2], studentId=row[3])
            for row in cursor.fetchall()
        ]
        print(payments)
        if payments:
            return render_template('payments.html', payments=payments,user=user)
        else:
            return render_template('error.html', error_message="No payments found")
    except Error as e:
        print(e)
        return render_template('error.html', error_message="An error occurred")
    finally:
        db_connection_close(cursor, conn)
# Route to create a new student
@payment_route.route('/payments', methods=['POST'])
def create_payment():
    amount = request.form['value']
    dateofpayment = request.form['paymentDate']
    studentId=request.form['studentId']
    # studentid=session['studentId']
    query = "INSERT INTO payments (Amount, DateOfPayment) Values (%s, %s);"
    query2 = "INSERT INTO studentsPayments (StudentId, PaymentId) Values (%s, %s);"
    conn = db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(query, (amount, dateofpayment))
        conn.commit()
        cursor.execute(query2, (studentId, cursor.lastrowid))
        conn.commit()
        return redirect('/payments')
        # return jsonify(message="Student added successfully"), 201
    except Error as e:
        return render_template('error.html', error_message=e)
    finally:
        db_connection_close(cursor, conn)
@payment_route.route('/link_payment', methods=['POST'])
def link_payment():
    studentId = request.form['studentId']
    paymentId = request.form['paymentId']
    query = """
    INSERT INTO studentsPayments (StudentId, PaymentId)
    Values (%s, %s);
    """

    conn = db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(query, (studentId, paymentId))
        conn.commit()
        return redirect('/payments')
        # return jsonify(message="Student added successfully"), 201
    except Error as e:
        return render_template('error.html', error_message=e)
    finally:
        db_connection_close(cursor, conn)

    
@payment_route.route('/delete_payment', methods=['POST'])
def delete_payment():
    payment_id=request.form['paymentId']
    student_id=request.form['studentId']
    
    print(f"payment:{payment_id}")
    query="""DELETE FROM studentsPayments WHERE StudentId = %s"""
    query2 = "DELETE FROM payments WHERE Id = %s"
    query3 = "DELETE FROM studentsPayments WHERE PaymentId = %s"
    conn = db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(query, (student_id,))
        conn.commit()
        cursor.execute(query2, (payment_id,))
        conn.commit()
        cursor.execute(query3, (student_id,))
        conn.commit()
        return redirect('/payments')
    except Error as e:
        print(e)
        return render_template('error.html', error_message=e)
    finally:
        db_connection_close(cursor, conn)