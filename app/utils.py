from email.header import Header
from email.mime.text import MIMEText

from flask_login import current_user
import os
import random
import string
import smtplib

from app import app
from PIL import Image
from wtforms import SelectMultipleField, widgets

# класс для поля с несколькими чекбоксами
class MultiCheckboxField(SelectMultipleField):
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()


def save_image(file, item):
    filename = ''.join(random.choices(string.ascii_lowercase + string.digits, k=15)) + '.' + (
        file.filename.split('.').pop())
    file.save(os.path.join(app.config['IMAGE_FOLDER'], filename))
    item.image_name = filename
    image = Image.open(os.path.join(app.config['IMAGE_FOLDER'], item.image_name))
    image.thumbnail((800, 800))
    image.save(os.path.join(app.config['THUMBNAIL_FOLDER'], item.image_name))


def send_email(subject, to_addr, from_addr, body_text):
    msg = MIMEText(body_text, 'plain', 'utf-8')
    msg['Subject'] = Header(subject, 'utf-8')
    msg['From'] = from_addr
    msg['To'] = to_addr

    server = smtplib.SMTP('smtp.gmail.com', 587, timeout=120)
    server.ehlo()
    server.starttls()
    server.login(app.config['MAIL_USER'], app.config['MAIL_PASSWORD'])
    server.sendmail(msg['From'], msg['To'], msg.as_string())
    server.quit()


def send_recovery_email(to_addr, recovery_word):
    subject = "My Glazes - восстановление пароля"
    to_addr = to_addr
    from_addr = "myglazes.info@gmail.com"
    body_text = "http://myglazes.ru/recovery/"+recovery_word
    send_email(subject, to_addr, from_addr, body_text)