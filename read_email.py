# Python 3.8.0
import re
import smtplib
import time
import imaplib
import email
import traceback
import datetime
import psycopg2
from email.header import decode_header
# -------------------------------------------------
#
# Utility to read email from Gmail Using Python
#
# ------------------------------------------------
ORG_EMAIL = "@gmail.com"
FROM_EMAIL = "padelcanaletes" + ORG_EMAIL
FROM_PWD = "saltsd'aigua2022"
SMTP_SERVER = "imap.gmail.com"
SMTP_PORT = 993


class PGConnection(object):

    def __init__(self):
        self.connection = psycopg2.connect(
            user='root',
            password='root',
            host='db',
            port='5432',
            database='verse_db'
        )

    def __enter__(self):
        self.cursor = self.connection.cursor()
        return self

    def __exit__(self, *args):
        self.cursor.close()
        self.connection.close()


def read_email_from_gmail():
    try:
        with PGConnection() as conn:
            conn.cursor.execute('CREATE TABLE IF NOT EXISTS verse_payments (timestamp integer PRIMARY KEY, usuario varchar(50), cantidad float)')
            conn.connection.commit()
        mail = imaplib.IMAP4_SSL(SMTP_SERVER)
        mail.login(FROM_EMAIL, FROM_PWD)
        mail.select('inbox')
        last_email_ids = []
        while True:
            try:
                mail.select('inbox')
                data = mail.search(None, 'ALL')
                mail_ids = data[1]
                id_list = mail_ids[0].split()
                if len(last_email_ids) < len(id_list):
                    new_emails = len(id_list) - len(last_email_ids)
                    print(str(new_emails) + ' new message/s recieved!\n|-|-|-|-|-|-|-|-|-|-|-|-|')
                    last_email_ids = id_list
                    first_email_id = int(id_list[-new_emails])
                    latest_email_id = int(id_list[-1])
                    for i in range(latest_email_id, first_email_id-1, -1):
                        data = mail.fetch(str(i), '(RFC822)')
                        for response_part in data:
                            arr = response_part[0]
                            if isinstance(arr, tuple):
                                msg = email.message_from_string(str(arr[1], 'utf-8'))
                                email_subject = msg['subject']
                                email_subject, _ = decode_header(email_subject)[0]
                                try:
                                    email_subject = email_subject.decode('utf-8')
                                except:
                                    pass
                                email_from = msg['from']
                                date = msg['date']
                                if re.search(r'\([A-Z]{3}\)', date):
                                    date = date[:-6]
                                try:
                                    date = datetime.datetime.strptime(date, "%a, %d %b %Y %H:%M:%S %z").timestamp()
                                except:
                                    date = datetime.datetime.strptime(date, "%a, %d %b %Y %H:%M:%S %Z").timestamp()
                                if "te ha enviado" in email_subject:
                                    usuario = email_subject.split(" te ha enviado ")[0]
                                    email_subject = email_subject.replace('\xa0', ' ')
                                    cantidad_str = email_subject.split(" te ha enviado ")[1].split(' ')[0].replace(',', '.')
                                    cantidad = float(cantidad_str)
                                    # Insert data to PostgreSQL
                                    with PGConnection() as conn:
                                        conn.cursor.execute('INSERT INTO verse_payments (timestamp, usuario, cantidad) VALUES (%s, %s, %s)', (date, usuario, cantidad))
                                        conn.connection.commit()
                                        print(f"[Data ok in database] - {date} - {usuario} - {cantidad}")
            except Exception as e:
                traceback.print_exc()
                print(str(e))
            time.sleep(60)
    except Exception as e:
        traceback.print_exc()
        print(str(e))


read_email_from_gmail()
