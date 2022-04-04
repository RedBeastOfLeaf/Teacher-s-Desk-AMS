from flask import Flask, render_template, redirect, request, flash, sessions, url_for
from flask_sqlalchemy import SQLAlchemy
import yaml

with open(r'./x.yaml') as file:
    important = yaml.load(file, Loader=yaml.FullLoader)

app = Flask(__name__)
app.secret_key = important['SECRET_KEY']
app.config['UPLOAD_FOLDER'] = important['UPLOAD_FOLDER']
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////databases/Teacher.db'
app.config['SQLALCHEMY_BINDS'] = {'Classroom' : 'sqlite:////databases/Classroom.db', 'Student' : 'sqlite:////databases/Student.db', 'Attendance_Record' : 'sqlite:////databases/Attendance_Record.db'}
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

#create teacher table
class Teacher(db.Model):
    teacher_id = db.Column(db.Integer, primary_key = True, nullable = False, unique=True)
    Fname = db.Column(db.String(100), nullable = False)
    Lname = db.Column(db.String(100), nullable = False)
    email = db.Column(db.String(100), nullable = False)
    password = db.Column(db.String(100), nullable = False)

#create classroom table
class Classroom(db.Model):
    __bind_key__ = 'Classroom'
    class_id = db.Column(db.Integer, primary_key = True, nullable = False, unique=True)
    class_name = db.Column(db.String(100), nullable = False)
    teacher_id = db.Column(db.Integer, db.ForeignKey('teacher.teacher_id'), nullable = False)
    subject_name = db.Column(db.String(100), nullable = False)
    batch_size = db.Column(db.Integer, nullable = False)
    class_taken = db.Column(db.Integer, nullable = False)
    attendance_id = db.Column(db.Integer, db.ForeignKey('attendance_record.attendance_id'), nullable = False)
    
#create student table
class Student(db.Model):
    __bind_key__ = 'Student'
    student_id = db.Column(db.Integer, primary_key = True, nullable = False, unique = True)
    Fname = db.Column(db.String(100), nullable = False)
    Lname = db.Column(db.String(100), nullable = False)
    roll = db.Column(db.Integer, nullable = False)
    dob = db.Column(db.Date, nullable = False)
    attendance_id = db.Column(db.Integer, db.ForeignKey('attendance_record.attendance_id'), nullable = False)

#create attendance_record table
class Attendance_Record(db.Model):
    __bind_key__ = 'Attendance_Record'
    attendance_id = db.Column(db.Integer, primary_key = True, nullable = False)
    student_id = db.Column(db.Integer, db.ForeignKey('student.student_id'), nullable = False)
    class_id = db.Column(db.Integer, db.ForeignKey('classroom.class_id'), nullable = False)
    days_present = db.Column(db.Integer, nullable = False)
    overall_percent = db.Column(db.Float, nullable=False)
    defaulter = db.Column(db.Boolean, default = False)
    roll_no = db.Column(db.Integer, nullable = False)
    status = db.Column(db.Integer, nullable = False)



#insert values in Teacher table
@app.route('/insert_teacher', methods=['POST'])
def insert_teacher():
    if request.method == 'POST':
        teacher_id = request.form['teacher_id']
        Fname = request.form['Fname']
        Lname = request.form['Lname']
        email = request.form['email']
        password = request.form['password']
        teacher = Teacher(teacher_id = teacher_id, Fname = Fname, Lname = Lname, email = email, password = password)
        db.session.add(teacher)
        db.session.commit()
        return redirect(url_for('teacher_login'))


@app.route('/teacher_login', methods=['GET', 'POST'])
def login():
    return render_template('teacher_login.html')

if __name__ == '__main__':
    app.run(debug=True)