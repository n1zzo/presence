#! /usr/bin/env python3

from db import DB
from sys import argv
import send
import time
import toml


def load_config():
    with open("config.toml") as config_file:
        return toml.loads(config_file.read())


def notify(code, email):
    config = load_config()
    print("Emailing " + code + " at email " + email)
    send.email(code, email, config)


def notify_all(section):
    config = load_config()
    students = []
    try:
        with DB(section) as db:
            students = db.get_students()
    except FileNotFoundError:
        print("Database section " + section + " does not exists!")
    for student in students:
        print("Emailing " + student["codice_persona"] +
              " at email " + student["email"])
        send.email(student["codice_persona"], student["email"], config)
        time.sleep(1)


def main():
    if len(argv) < 2:
        print("""Usage: ./main.py [OPTION]

Options:
--import CSV SECTION              import the csv containing student infos
--notify CODE EMAIL         send the qr-code to the selected email
--notify-all SECTION        send the qr-code to the students of a section""")
        return
    else:
        if "import" in argv[1] and len(argv) >= 4:
            section = argv[3]
            dbname = 'data/students_'+section+'.db'
            # Create database if not exists
            open(dbname, 'a').close()
            with DB(section) as db:
                db.import_students(argv[2])
        elif argv[1] == "--notify":
            notify(argv[2], argv[3])
        elif argv[1] == "--notify-all" and len(argv) >= 3:
            section = argv[2]
            notify_all(section)
        else:
            print("Error: unknown command line parameters")


if __name__ == "__main__":
    main()
