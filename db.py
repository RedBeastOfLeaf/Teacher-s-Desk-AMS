import sqlite3
import re
#create database
def create_db(c, conn):
    c.execute('''CREATE TABLE Attendance_Records
	student_id	INTEGER NOT NULL FOREIGN KEY REFERENCES Student_Record(student_id),
	class_id	INTEGER NOT NULL FOREIGN KEY REFERENCES Classroom(class_id),
	days_present	INTEGER NOT NULL,
	overall_percent	REAL NOT NULL,
	defaulter	BLOB DEFAULT 0,
	roll_no	INTEGER NOT NULL,
	attendance_id PRIMARY KEY AUTOINCREMENT INTEGER NOT NULL UNIQUE)''')
    conn.commit()

#insert data
def insert_data(c, conn, name, roll, present):
    c.execute("INSERT INTO attendance(name, roll, present) VALUES (?, ?, ?)", (name, roll, present))
    conn.commit()

#check if data exists
def check_data(c, conn, roll):
    c.execute("SELECT * FROM t_desk WHERE roll = ?", (roll,))
    conn.commit()
    return c.fetchone()

#create table named attendance
def create_table(c, conn):
    c.execute("CREATE TABLE attendance(id INTEGER PRIMARY KEY, name TEXT, roll INTEGER, present INTEGER)")
    conn.commit()
#check if database is connected
def check_db(c, conn):
    try:
        c.execute("SELECT * FROM t_desk")
        conn.commit()
        return True
    except:
        return False