#! /usr/bin/env python3

import sqlite3
import csv
import time
import os.path
from collections import namedtuple


Student = namedtuple("student",
                     "codice_persona matricola nome email sessions")

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
        c.execute('''CREATE TABLE IF NOT EXISTS students
                     (codice_persona text, matricola text,
                      nome text, email text)''')
        c.execute('''CREATE TABLE IF NOT EXISTS registrations
                     (codice_persona TEXT, lab_id INTEGER, timestamp INTEGER,
                      UNIQUE(codice_persona, lab_id))''')
        c.execute('''CREATE TABLE IF NOT EXISTS analytics
                     (codice_persona TEXT, lab_id INTEGER,
                      begin INTEGER, end INTEGER,
                      UNIQUE(codice_persona, lab_id, begin))''')
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
            student = Student(*(row[0:4] + ([], )))._asdict()
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

    def import_students(self, csv_path):
        self.create_tables()
        c = self.conn.cursor()
        with open(csv_path) as csv_file:
            students_reader = csv.reader(csv_file)
            for student in students_reader:
                s = Student(*(student + [None]))
                t = (s.codice_persona, s.matricola, s.nome, s.email)
                c.execute("INSERT INTO students VALUES (?, ?, ?, ?)", t)
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


def main():
    db = DB()
    db.import_students("elenco_studenti.csv")


if __name__ == "__main__":
    main()
