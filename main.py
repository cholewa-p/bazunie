import mysql.connector


con=mysql.connector.connect(
    user='root',
    host='localhost',
    database='newname',
    passwd='qwerty'
)

cur=con.cursor()

cur.execute(" CREATE TABLE customers (name VARCHAR(255), id int); ")

con.commit()