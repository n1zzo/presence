#! /usr/bin/env python3


import send
from sys import argv
from db import DB

config = None


def notify_all():
    students = []
    with DB() as db:
        students = db.get_students()
    for student in students:
        send.email(student["codice_persona"], student["email"], config)


def main():
    if len(argv) < 2:
        print("Usage: ./main.py <csv_to_import>")
        return
    else:
        with DB() as db:
            db.import_students(argv[1])


if __name__ == "__main__":
    main()
