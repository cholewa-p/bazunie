from flask import Flask, request, redirect, jsonify, render_template, Blueprint
from mysql.connector import Error
from database import db_connection, db_connection_close

payment_route = Blueprint('payment', __name__)
@payment_route.route('/payments', methods=['GET'])
def get_payments():
    conn = db_connection()
    cursor = conn.cursor()
    query = """SELECT p.Amount ,s.FirstName ,s.LastName ,p.DateOfPayment ,s.Id ,p.Id  from studentsPayments sp 
            inner join students s on s.Id =sp.StudentId 
            inner join payments p on p.Id =sp.PaymentId;
    """
    try:
        cursor.execute(query)
        payments = [
            dict(amount=row[0], firstName=row[1], lastName=row[2], dateOfPayment=row[3],studentId=row[4],paymentId=row[5])
            for row in cursor.fetchall()
        ]
        print(payments)
        if payments:
            return render_template('payments.html', payments=payments)
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
    amount = request.form['amount']
    dateofpayment = request.form['dateofpayment']
    query = """
    INSERT INTO payments (Amount, DateOfPayment)
    Values (%s, %s);
    """

    conn = db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(query, (amount, dateofpayment))
        conn.commit()
        return redirect('/payments')
        # return jsonify(message="Student added successfully"), 201
    except Error as e:
        return render_template('error.html', error_message=e)
    finally:
        db_connection_close(cursor, conn)
# Route to delete a student
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

    
@payment_route.route('/delete_payment/<int:payment_id>', methods=['POST'])
def delete_payment(payment_id):
    payment_id = str(payment_id)
    # request.form.get['student_id']
    print(payment_id)
    query = "DELETE FROM payments WHERE Id = %s"
    conn = db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(query, (payment_id,))
        conn.commit()
        if cursor.rowcount > 0:
            return redirect('/payments')
        else:
            return jsonify(message="payment not found"), 404
    except Error as e:
        print(e)
        return jsonify(message="An error occured"), 500
    finally:
        db_connection_close(cursor, conn)

# Route to update a student
@payment_route.route('/update_payment/<int:payment_id>', methods=['POST'])
def update_payment(payment_id):
    payment_id = str(payment_id)

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

    values.append(payment_id)  # append the student id to the values list
    set_clause = ', '.join(fields)
    query = f"UPDATE payments SET {set_clause} WHERE Id = %s"

    try:
        cursor.execute(query, values)
        conn.commit()
        if cursor.rowcount > 0:
            return redirect('/payments')
        else:
            return jsonify(message="payment not found"), 404
    except Error as e:
        print(e)
        return jsonify(message="An error occurred"), 500
    finally:
        db_connection_close(cursor, conn)
