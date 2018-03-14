#! /usr/bin/env python3

from email.message import EmailMessage
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import pyqrcode
import smtplib


def email(code, recipient, config):
    msg = EmailMessage()
    msg = MIMEMultipart('alternative')
    msg['Subject'] = 'QR Code per la registrazione al laboratorio'
    msg['From'] = config["SMTP"]["sender"]
    msg['To'] = recipient

    text = """Il tuo client email non supporta le email basate su HTML.
    Per registrarti al laboratorio fornisci questo codice: {}""".format(code)
    html = """\
    <html>
      <head></head>
      <body>
        <p>
        <h3>
            Mostra questo qr-code ai responsabili di laboratorio per
            registrarti.
        </h3>
        </p>
        <p>
           <img src="cid:qrcode">
        </p>
      </body>
    </html>
    """

    part1 = MIMEText(text, 'plain')
    part2 = MIMEText(html, 'html')

    part3 = MIMEImage(create_qrcode(code))
    part3.add_header('Content-ID', '<qrcode>')

    msg.attach(part1)
    msg.attach(part2)
    msg.attach(part3)

    s = smtplib.SMTP(config["SMTP"]["server"])
    s.starttls()
    s.login(config["SMTP"]["login"], config["SMTP"]["password"])
    s.send_message(msg)
    s.quit()


def create_qrcode(data):
    qr = pyqrcode.create(data)
    qr.png("code.png", scale=12, module_color=[0xF4, 0x22, 0x72], background=[0x20, 0x20, 0x20])
    with open("code.png", "rb") as f:
        return f.read()
