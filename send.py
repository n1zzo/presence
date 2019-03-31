#! /usr/bin/env python3

from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import pyqrcode
import smtplib


def email(code, recipient, config):
    # Create message container.
    msg = MIMEMultipart('related')
    msg['Subject'] = 'QR Code per la registrazione al laboratorio'
    msg['From'] = config["SMTP"]["sender"]
    msg['To'] = recipient

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

        Ricordati di compilare il Google form con i dati del tuo gruppo,
        sono un membro del gruppo deve compilarlo, con i dati di tutti e tre
        i componenti.

        Il form lo trovate al seguente url: <a href="https://goo.gl/forms/HSIQ9z6jpsgQIoVz1">https://goo.gl/forms/HSIQ9z6jpsgQIoVz1</a>
      </body>
    </html>
    """

    msgHtml = MIMEText(html, 'html')
    msgImg = MIMEImage(create_qrcode(code), name="qrcode.png")
    msgImg.add_header('Content-ID', '<qrcode>')
    msgImg.add_header('Content-Disposition',
                      'attachment',
                      filename="qrcode.png")
    msgImg.add_header('Content-Disposition',
                      'inline',
                      filename="qrcode.png")

    msg.attach(msgHtml)
    msg.attach(msgImg)

    while True:
        try:
            s = smtplib.SMTP(config["SMTP"]["server"])
            s.starttls()
            s.login(config["SMTP"]["login"], config["SMTP"]["password"])
            s.send_message(msg)
            s.quit()
            break
        except Exception as e:
            print(str(e)+"...retrying!")
            continue


def message(subject, text, recipient, config):
    msg = MIMEText(text)
    msg['Subject'] = subject
    msg['From'] = config["SMTP"]["sender"]
    msg['To'] = recipient

    while True:
        try:
            s = smtplib.SMTP(config["SMTP"]["server"])
            s.starttls()
            s.login(config["SMTP"]["login"], config["SMTP"]["password"])
            s.send_message(msg)
            s.quit()
            break
        except Exception as e:
            print(str(e)+"...retrying!")
            continue


def create_qrcode(data):
    qr = pyqrcode.create(data)
    qr.png("code.png",
           scale=12,
           module_color=[0x00, 0x00, 0x00],
           background=[0xff, 0xff, 0xff])
    with open("code.png", "rb") as f:
        return f.read()
