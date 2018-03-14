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


def notify_all():
    config = load_config()
    students = []
    with DB() as db:
        students = db.get_students()
    for student in students:
        print("Emailing "+student["codice_persona"]+" at email "+student["email"])
        send.email(student["codice_persona"], student["email"], config)
        time.sleep(1)


def main():
    if len(argv) < 2:
        print("""Usage: ./main.py [OPTION]

Options:
--import CSV                import the csv containing student infos
--notify CODE EMAIL         send the qr-code to the selected email
--notify-all                send the qr-code to all the students""")
        return
    else:
        if "import" in argv[1]:
            with DB() as db:
                db.import_students(argv[2])
        elif argv[1] == "--notify":
            notify(argv[2], argv[3])
        elif argv[1] == "notify-all":
            notify_all()
        else:
            print("Error: unknown command line parameters")


if __name__ == "__main__":
    main()
