import os
import string
import random

from datetime import datetime


from sqlalchemy import func

from app import app
from PIL import Image

from app.models import Material, Item, ItemGlaze, ItemImage


# присвоение картинки уникального имени и сохранение её на диске
def save_image(file, image):
    filename = ''.join(random.choices(string.ascii_lowercase + string.digits, k=15)) + '.' + (
        file.filename.split('.').pop())
    file.save(os.path.join(app.config['IMAGE_FOLDER'], filename))
    image.name = filename
    image_file = Image.open(os.path.join(app.config['IMAGE_FOLDER'], image.name))
    image_file.thumbnail((800, 800))
    image_file.save(os.path.join(app.config['THUMBNAIL_FOLDER'], image.name))


def save_item(item_id, form, db):
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
            save_image(image_file, image)
            db.session.add(image)
            image_id = db.session.query(func.max(Image.id)).scalar()
            item_image = ItemImage(image_id=image_id, item_id=item_id, order=next_order)
            next_order += 1
            db.session.add(item_image)
    db.session.commit()
