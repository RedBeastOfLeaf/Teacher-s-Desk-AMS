from flask import Flask, render_template, redirect, request, flash, sessions, url_for
import yaml
import os
# import cv2
import easyocr
# import matplotlib.pyplot as plt
import re
import sqlite3
from flask_sqlalchemy import SQLAlchemy

with open(r'./x.yaml') as file:
    important = yaml.load(file, Loader=yaml.FullLoader)

app = Flask(__name__)
app.secret_key = important['SECRET_KEY']
app.config['UPLOAD_FOLDER'] = important['UPLOAD_FOLDER']
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database/Teacher.db'
app.config['SQLALCHEMY_BINDS'] = {'classroom' : 'sqlite:///database/Classroom.db', 'student' : 'sqlite:///database/Student.db', 'attendance_record' : 'sqlite:///database/Attendance_Record.db'}
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
    __bind_key__ = 'classroom'
    class_id = db.Column(db.Integer, primary_key = True, nullable = False, unique=True)
    class_name = db.Column(db.String(100), nullable = False)
    teacher_id = db.Column(db.Integer, db.ForeignKey('teacher.teacher_id'), nullable = False)
    subject_name = db.Column(db.String(100), nullable = False)
    batch_size = db.Column(db.Integer, nullable = False)
    class_taken = db.Column(db.Integer, nullable = False)
    

#create student table
class Student(db.Model):
    __bind_key__ = 'student'
    student_id = db.Column(db.Integer, primary_key = True, nullable = False, unique = True)
    Fname = db.Column(db.String(100), nullable = False)
    Lname = db.Column(db.String(100), nullable = False)
    roll = db.Column(db.Integer, nullable = False)
    dob = db.Column(db.Date, nullable = False)

#create attendance_record table
class Attendance_Record(db.Model):
    __bind_key__ = 'attendance_record'
    attendance_id = db.Column(db.Integer, primary_key = True, nullable = False)
    student_id = db.Column(db.Integer, db.ForeignKey('student.student_id'), nullable = False)
    class_id = db.Column(db.Integer, db.ForeignKey('classroom.class_id'), nullable = False)
    days_present = db.Column(db.Integer, nullable = False)
    overall_percent = db.Column(db.Float, nullable=False)
    defaulter = db.Column(db.Boolean, default = False)
    roll_no = db.Column(db.Integer, nullable = False)
    status = db.Column(db.Integer, nullable = False)


def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in important['ALLOWED_EXTENSIONS']

def recognize_text(img_path):
    reader = easyocr.Reader(['en'])
    return reader.readtext(img_path)

def extract_numbers(string):
    return re.findall("[0-9]+._.[a-z]+|[0-9]+._.[A-Z]+|[0-9]+ [A-Z]+|[0-9]+._.", string)

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        if 'files[]' not in request.files or request.files['files[]'].filename == '':
            flash('No file found')
            return redirect(request.url)
        
        files = request.files.getlist('files[]')

        i = 1

        total_batch_size = 73
        absent = []
        Present = list()


        for img in files:
            filename = 'check' + str(i) + '.' + img.filename.rsplit('.')[1]

            if img and allowed_file(img.filename):
                img.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            else:
                flash('Not the right file format')
            i += 1
        
            img_path = important['UPLOAD_FOLDER'] + filename

            result = recognize_text(img_path)

            result = str(result)
            result = result.replace('-', '_')

            present = extract_numbers(result)

            present = re.findall("[1-9]+", str(present))

            present = set(map(int, present))

            Present.extend(list(present))


            # absent.append(map(lambda x: x if x not in absent else None,  [i for i in range(1, total_batch_size) if i not in present]))

            # absent.extend([i for i in range(1, total_batch_size) if i not in present])
            # absent = [i for i in range(1, total_batch_size) if i not in present]

        Present = set(Present)

        absent = [j for j in range(1, total_batch_size) if j not in Present]

        flash("Present Roll Numbers: " + str(Present))
        flash("Absent Roll Numbers: " + str(set(absent)))
        flash("Total Absentees: " + str(len(set(absent))))

    return render_template('home.html')

#create values in teacher table
@app.route('/insert')
def insert():
    teacher = Teacher(Fname="Vishal", Lname="Thakur", email="vishalthakur@gmail.com", password="vishal")
    db.session.add(teacher)
    db.session.commit()
    return "Inserted"


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == "POST":
        if 'email' in request.form and 'password' in request.form:
            email = request.form['email']
            password = request.form['password']

            if email == 'admin@gmail.com' and password == 'root':
                return "Admin Logged In"
            
            t = Teacher.query.filter_by(email=email).first()
            if t == None:
                return "Wrong login credentials"
            elif t.password == password:
                return redirect(url_for('home'))
            return "Wrong login credentials"
        return "Wrong login credentials"
    return render_template('login.html')

if __name__ == '__main__':
    app.run(debug=True)