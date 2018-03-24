#! /usr/bin/env python3

import sqlite3
import csv
import time
import os.path
from collections import namedtuple


Student = namedtuple("student",
                     "codice_persona matricola nome email")


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
            students.append(Student(row[0], row[1], row[2], row[3])._asdict())
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
            students.append(Student(row[0], row[1], row[2], row[3])._asdict())
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
            students.append(Student(row[0], row[1], row[2], row[3])._asdict())
        self.conn.commit()
        return students

    def import_students(self, csv_path):
        self.create_tables()
        c = self.conn.cursor()
        with open(csv_path) as csv_file:
            students_reader = csv.reader(csv_file)
            for student in students_reader:
                s = Student(student[0], student[1], student[2], student[3])
                t = (s.codice_persona, s.matricola, s.nome, s.email)
                c.execute("INSERT INTO students VALUES (?, ?, ?, ?)", t)
        self.conn.commit()

    def register(self, student_id, lab_id):
        c = self.conn.cursor()
        t = (student_id, lab_id, int(time.time()))
        c.execute("INSERT OR IGNORE INTO registrations VALUES (?, ?, ?)", t)
        self.conn.commit()

    def timer_start(self, student_id, lab_id):
        c = self.conn.cursor()
        t = (student_id, lab_id, int(time.time()), None)
        c.execute("INSERT OR IGNORE INTO analytics VALUES (?, ?, ?, ?)", t)
        self.conn.commit()

    def timer_stop(self, student_id, lab_id):
        c = self.conn.cursor()
        t = (int(time.time()), lab_id, student_id)
        c.execute("UPDATE analytics "
                  "SET end = ? WHERE begin IS NOT NULL AND lab_id = ? "
                  "AND codice_persona = ?", t)
        self.conn.commit()


def main():
    db = DB()
    db.import_students("elenco_studenti.csv")


if __name__ == "__main__":
    main()
