from flask import Flask, render_template
from student import student_route
from lecturer import lecturer_route
from enrollment import enrollment_route
app = Flask(__name__)
app.register_blueprint(student_route)
app.register_blueprint(lecturer_route)
app.register_blueprint(enrollment_route)
#Route to main page
@app.route('/')
def index():
    return render_template('./index.html')

if __name__ == '__main__':
    app.run(debug=True)