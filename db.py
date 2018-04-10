#! /usr/bin/env python3

import sqlite3
import csv
import time
import os.path
from collections import namedtuple


Student = namedtuple("student",
                     "codice_persona matricola nome email gruppo sessions")

Session = namedtuple("session", "begin end")


class DB:

    section = None
    conn = None

    def __init__(self, section):
        self.section = section

    def __enter__(self):
        dbname = 'data/students_'+self.section+'.db'
        if not os.path.isfile(dbname):
            raise FileNotFoundError
        self.conn = sqlite3.connect(dbname)
        #self.conn.set_trace_callback(print)
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.conn.close()

    def create_tables(self):
        c = self.conn.cursor()
        # Create table
        c.execute('''CREATE TABLE IF NOT EXISTS students (
                     codice_persona text, matricola text,
                     nome text, email text, `group` INTEGER)''')
        c.execute('''CREATE TABLE IF NOT EXISTS registrations (
                     codice_persona TEXT, lab_id INTEGER, timestamp INTEGER,
                     UNIQUE(codice_persona, lab_id))''')
        c.execute('''CREATE TABLE IF NOT EXISTS analytics (
                     codice_persona TEXT, lab_id INTEGER,
                     begin INTEGER, end INTEGER,
                     UNIQUE(codice_persona, lab_id, begin))''')
        c.execute('''CREATE TABLE IF NOT EXISTS groups (
                     id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                     codice_1 TEXT NOT NULL,
                     codice_2 TEXT NOT NULL,
                     codice_3 TEXT)''')
        c.execute('''CREATE TABLE IF NOT EXISTS groupinfo (
                     id INTEGER NOT NULL PRIMARY KEY,
                     score INTEGER,
                     repo TEXT,
                     compiles INTEGER,
                     passed_tests INTEGER)''')
        self.conn.commit()

    def get_students(self, student_id=None):
        students = []
        c = self.conn.cursor()
        if student_id is None:
            c.execute('SELECT * FROM students')
        else:
            t = (student_id,)
            c.execute('SELECT * FROM students '
                      'WHERE codice_persona = ?', t)
        rows = c.fetchall()
        for row in rows:
            student = Student(*(row + ([], )))._asdict()
            students.append(student)
        self.conn.commit()
        return students

    def get_registered(self, lab_id):
        students = []
        c = self.conn.cursor()
        t = (lab_id, )
        c.execute('SELECT * FROM students '
                  'NATURAL JOIN registrations '
                  'WHERE lab_id = ? '
                  'ORDER BY timestamp', t)
        rows = c.fetchall()
        for row in rows:
            student = Student(*(row[0:5] + ([], )))._asdict()
            # Extract sessions from DB
            t = (student["codice_persona"], lab_id)
            c.execute('SELECT begin, end FROM analytics '
                      'WHERE codice_persona = ? AND lab_id = ?', t)
            s_rows = c.fetchall()
            for s_row in s_rows:
                student["sessions"].append(Session(s_row[0],
                                                   s_row[1])._asdict())
            students.append(student)
        self.conn.commit()
        return students

    def get_not_yet_registered(self, lab_id):
        students = []
        c = self.conn.cursor()
        t = (lab_id, )
        c.execute('SELECT * '
                  'FROM students s '
                  'WHERE NOT EXISTS (SELECT NULL '
                  'FROM registrations r '
                  'WHERE s.codice_persona = r.codice_persona '
                  'AND r.lab_id = ?)', t)
        rows = c.fetchall()
        for row in rows:
            students.append(Student(*(row + ([], )))._asdict())
        self.conn.commit()
        return students

    def get_groups(self):
        students = []
        c = self.conn.cursor()
        c.execute('SELECT id, codice_persona, nome, email '
                  'FROM groups, students '
                  'WHERE codice_1 == codice_persona '
                  'OR codice_2 == codice_persona '
                  'OR codice_3 == codice_persona;')
        rows = c.fetchall()
        for row in rows:
            students.append(row)
        self.conn.commit()
        return students

    def import_students(self, csv_path):
        self.create_tables()
        c = self.conn.cursor()
        with open(csv_path) as csv_file:
            students_reader = csv.reader(csv_file)
            for student in students_reader:
                s = Student(*(student + 2 * [None]))
                t = (s.codice_persona,
                     s.matricola,
                     s.nome,
                     s.email,
                     s.gruppo)
                c.execute("INSERT INTO students VALUES (?, ?, ?, ?, ?)", t)
        self.conn.commit()

    def register(self, student_id, lab_id):
        c = self.conn.cursor()
        t = (student_id, lab_id, int(time.time()))
        c.execute("INSERT OR IGNORE INTO registrations VALUES (?, ?, ?)", t)
        self.conn.commit()

    def timer(self, action, student_id, lab_id):
        c = self.conn.cursor()
        if action == "start":
            t = (student_id, lab_id, int(time.time()), None)
            c.execute("INSERT OR IGNORE INTO analytics VALUES (?, ?, ?, ?)", t)
        elif action == "stop":
            t = (int(time.time()), lab_id, student_id)
            c.execute("UPDATE analytics "
                      "SET end = ? WHERE begin IS NOT NULL AND end is NULL "
                      "AND lab_id = ? AND codice_persona = ?", t)
        self.conn.commit()

    def import_groups(self, csv_path):
        self.create_tables()
        c = self.conn.cursor()
        with open(csv_path) as groups_csv:
             groups_reader = csv.reader(groups_csv)
             for group in groups_reader:
                 t = tuple(group[3:6])
                 c.execute("INSERT OR IGNORE INTO groups"
                           "(codice_1, codice_2, codice_3)"
                           "VALUES (?, ?, ?)", t)
        self.conn.commit()

    def import_repos(self, csv_path):
        self.create_tables()
        c = self.conn.cursor()
        with open(csv_path) as groups_csv:
             groups_reader = csv.reader(groups_csv)
             for group in groups_reader:
                 print(group)
                 t = (group[1], group[0])
                 c.execute("UPDATE groupinfo "
                           "SET repo = ? "
                           "WHERE id = ?", t)
        self.conn.commit()

    def get_groups(self):
        groups = []
        c = self.conn.cursor()
        c.execute('SELECT * FROM groups')
        rows = c.fetchall()
        for row in rows:
            group = {}
            group["id"] = row[0]
            group["members"] = []
            for member_id in row[1:4]:
                if member_id is not "":
                    student = self.get_students(student_id=member_id)
                    group["members"].extend(student)
            groups.append(group)
        self.conn.commit()
        return groups

    def get_group_info(self, group_id):
        groups = []
        c = self.conn.cursor()
        t = (group_id,)
        c.execute('SELECT * FROM groupinfo '
                  'WHERE id = ?', t)
        rows = c.fetchall()
        for row in rows:
            group = {}
            group["id"] = row[0]
            group["score"] = row[1]
            group["repo"] = row[2]
            group["compiles"] = row[3]
            group["passed_tests"] = row[4]
            group["sessions"] = []
            groups.append(group)
        self.conn.commit()
        return groups
