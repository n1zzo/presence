#! /usr/bin/env python3

from db import DB
from sys import argv
from pprint import pprint
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


def notify_groups(section):
    config = load_config()
    students = []
    email = ""
    with open("email_gruppo_2.txt", "r") as f:
        template = f.read()
    try:
        with DB(section) as db:
            students = db.get_groups()
    except FileNotFoundError:
        print("Database section " + section + " does not exists!")
    for i in range(0, len(students), 1):
        s1 = students[i]
        s2 = students[i+1]
        s3 = students[i+2]
        if s1[0] in {58, 61, 62, 63}:
            email = template.format(numero_gruppo=s1[0],
                                    nome1=s1[2], codice_persona1=s1[1],
                                    nome2=s2[2], codice_persona2=s2[1],
                                    nome3=s3[2], codice_persona3=s3[1])
            print("[Prova Finale] Obiettivi da Completare entro 06/04/18",
                         email,
                         s1[3],
                         config)
            print("[Prova Finale] Obiettivi da Completare entro 06/04/18",
                         email,
                         s2[3],
                         config)
            print("[Prova Finale] Obiettivi da Completare entro 06/04/18",
                         email,
                         s3[3],
                         config)


def main():
    if len(argv) < 2:
        print("""Usage: ./main.py [OPTION]

Options:
--import        CSV SECTION    import the csv containing student infos
--import-groups CSV SECTION    import the csv containing student groups
--notify        CODE EMAIL     send the qr-code to the selected email
--notify-all    SECTION        send the qr-code to the students of a section
--notify-groups SECTION        notify groups about something""")
        return
    else:
        if argv[1] == "--import" and len(argv) >= 4:
            section = argv[3]
            dbname = 'data/students_'+section+'.db'
            # Create database if not exists
            open(dbname, 'a').close()
            with DB(section) as db:
                db.import_students(argv[2])
        elif argv[1] == "--import-groups" and len(argv) >= 4:
            section = argv[3]
            with DB(section) as db:
                db.import_groups(argv[2])
        elif argv[1] == "--notify":
            notify(argv[2], argv[3])
        elif argv[1] == "--notify-all" and len(argv) >= 3:
            section = argv[2]
            notify_all(section)
        elif argv[1] == "--notify-groups" and len(argv) >= 3:
            section = argv[2]
            notify_groups(section)
        else:
            print("Error: unknown command line parameters")


if __name__ == "__main__":
    main()
