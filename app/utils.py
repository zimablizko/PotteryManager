from flask_login import current_user
import os
import random
import string

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
    print(filename)
    file.save(os.path.join(app.config['IMAGE_FOLDER'], filename))
    item.image_name = filename
    image = Image.open(os.path.join(app.config['IMAGE_FOLDER'], item.image_name))
    image.thumbnail((800, 800))
    image.save(os.path.join(app.config['THUMBNAIL_FOLDER'], item.image_name))