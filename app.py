from flask import Flask, render_template, redirect, request, flash, sessions, url_for
import yaml
import os
# import cv2
import easyocr
# import matplotlib.pyplot as plt
import re
import sqlite3

with open(r'./x.yaml') as file:
    important = yaml.load(file, Loader=yaml.FullLoader)

app = Flask(__name__)
app.secret_key = important['SECRET_KEY']
app.config['UPLOAD_FOLDER'] = important['UPLOAD_FOLDER']

def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in important['ALLOWED_EXTENSIONS']

def recognize_text(img_path):
    reader = easyocr.Reader(['en'])
    return reader.readtext(img_path)

def extract_numbers(string):
    return re.findall("[0-9]+._.[a-z]+|[0-9]+._.[A-Z]+|[0-9]+ [A-Z]+|[0-9]+._.", string)

#connect to database
def connect_db():
    conn = sqlite3.connect(important['t-desk.db'])
    c = conn.cursor()
    return c, conn

#check if database is connected
def check_db(c, conn):
    try:
        c.execute("SELECT * FROM t_desk")
        conn.commit()
        return True
    except:
        return False    


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

            present = re.findall("[0-9]+", str(present))

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

#take input into database and fetch data from database
@app.route('/attendance', methods=['GET', 'POST'])
def attendance():
    conn = sqlite3.connect(important['t-desk.db'])
    posts = conn.execute('SELECT * FROM t-desk').fetchall()
    conn.close()
    return posts


@app.route('/login')
def login():
    return render_template('login.html')

if __name__ == '__main__':
    app.run(debug=True)