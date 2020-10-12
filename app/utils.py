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


def save_image(file, image):
    filename = ''.join(random.choices(string.ascii_lowercase + string.digits, k=15)) + '.' + (
        file.filename.split('.').pop())
    file.save(os.path.join(app.config['IMAGE_FOLDER'], filename))
    image.name = filename
    image_file = Image.open(os.path.join(app.config['IMAGE_FOLDER'], image.name))
    image_file.thumbnail((800, 800))
    image_file.save(os.path.join(app.config['THUMBNAIL_FOLDER'], image.name))


def send_email(subject, to_addr, from_addr, body_text):
    msg = MIMEText(body_text, 'plain', 'utf-8')
    msg['Subject'] = Header(subject, 'utf-8')
    msg['From'] = from_addr
    msg['To'] = to_addr

    server = smtplib.SMTP('smtp.gmail.com', 587, timeout=120)
    server.ehlo()
    server.starttls()
    server.login(app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'])
    server.sendmail(msg['From'], msg['To'], msg.as_string())
    server.quit()


def send_recovery_email(to_addr, recovery_word):
    subject = "My Glazes - восстановление пароля"
    to_addr = to_addr
    from_addr = "myglazes.info@gmail.com"
    body_text = "http://myglazes.ru/recovery/"+recovery_word
    send_email(subject, to_addr, from_addr, body_text)

def save_item(d):
    item = db.session.query(Item).filter(Item.id == item_id).one()
    if not form.name.data:
        item.name = db.session.query(Material).filter_by(id=item.clay_id).first().name + ': '
    else:
        item.name = form.name.data
    item.description = form.description.data
    item.temperature = form.temperature.data
    item.clay_id = form.clay_id.data
    item.is_public = form.is_public.data
    item.edit_date = datetime.utcnow()
    for i, item_glaze in enumerate([None] * app.config['GLAZE_MAX_COUNT']):
        item_glaze = db.session.query(ItemGlaze).filter(ItemGlaze.item_id == item_id).filter(
            ItemGlaze.order == i).one_or_none()
        if form.glaze_list[i].data > 0:
            if item_glaze:
                item_glaze.glaze_id = form.glaze_list[i].data
            else:
                item_glaze = ItemGlaze(glaze_id=form.glaze_list[i].data, item_id=item_id, order=i)
                db.session.add(item_glaze)
            if not form.name.data:
                if i > 0:
                    item.name += ' + '
                item.name += db.session.query(Material).filter_by(id=form.glaze_list[i].data).first().name
        else:
            if item_glaze:
                db.session.delete(item_glaze)
    # Обработка изображений
    image_list = form.images.data
    next_order = 0
    if db.session.query(ItemImage).filter(ItemImage.item_id == item_id).all():
        next_order = db.session.query(func.max(ItemImage.order)).filter(ItemImage.item_id == item_id).scalar() + 1
    print(image_list)
    for image_file in image_list:
        if image_file:
            image = Image()
            utils.save_image(image_file, image)
            db.session.add(image)
            image_id = db.session.query(func.max(Image.id)).scalar()
            item_image = ItemImage(image_id=image_id, item_id=item_id, order=next_order)
            next_order += 1
            db.session.add(item_image)
    db.session.commit()