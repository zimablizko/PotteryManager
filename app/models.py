import random
import string
from datetime import datetime, timedelta

from flask_login import UserMixin
from sqlalchemy import desc, cast, Date, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, session, load_only
from werkzeug.security import generate_password_hash, check_password_hash

from app import db, login


# =Base = declarative_base()

class MaterialType(db.Model):
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    name = db.Column(db.String(64))

    def __repr__(self):
        return 'MaterialType {}'.format(self.name)


class Material(db.Model):
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    name = db.Column(db.String(64))
    type_id = db.Column(db.Integer, db.ForeignKey('material_type.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    create_date = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    edit_date = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    delete_date = db.Column(db.DateTime, index=True)

    def __repr__(self):
        return 'Material {}'.format(self.name)

    def get_type(self):
        return MaterialType.query.filter_by(id=self.type_id).first().name

    def check_in_use(self):
        check_clay = Item.query.filter(Item.delete_date == None).filter(Item.clay_id == self.id).all()
        check_glaze = Item.query.join(ItemGlaze).filter(ItemGlaze.glaze_id == self.id).filter(Item.delete_date == None).all()
        if len(check_glaze) > 0 or len(check_clay) > 0:
            return True
        else:
            return False


class ItemGlaze(db.Model):
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    glaze_id = db.Column(db.Integer, db.ForeignKey('material.id'))
    item_id = db.Column(db.Integer, db.ForeignKey('item.id'))
    order = db.Column(db.Integer)


class Item(db.Model):
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    name = db.Column(db.String(256))
    description = db.Column(db.Text(512))
    clay_id = db.Column(db.Integer, db.ForeignKey('material.id'))
    temperature = db.Column(db.Integer)
    image_name = db.Column(db.String(256))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    create_date = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    edit_date = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    delete_date = db.Column(db.DateTime, index=True)
    is_public = db.Column(db.Boolean)

    def __repr__(self):
        return 'Item {}, {}, delete:{}'.format(self.id, self.name, self.delete_date)

    def get_author(self):
        return User.query.filter_by(id=self.user_id).first()

    def get_main_image(self):
        item_image = ItemImage.query.filter_by(item_id=self.id).order_by(ItemImage.order).first()
        if item_image:
            return Image.query.filter_by(id=item_image.image_id).first().name
        else:
            return self.image_name

    def get_images(self):
        images_id_list = db.session.query(ItemImage.image_id).filter_by(item_id=self.id).order_by(ItemImage.order).all()
        if images_id_list:
            images = []
            # такой бред, потому что возвращаются туплы
            for image_id, in images_id_list:
                image = db.session.query(Image).filter_by(id=str(image_id)).first()
                images.append(image)
            print(images)
            return images
        return []

    def get_edit_date(self):
        if self.edit_date > self.create_date:
            return self.edit_date.date()
        else:
            return self.create_date.date()

    def get_clay_name(self):
        clay = Material.query.join(Item).filter(Item.id == self.id).first()
        if clay:
            return clay.name
        else:
            return None

    def get_glazes(self):
        glazes = Material.query.join(ItemGlaze).filter(ItemGlaze.item_id == self.id).all()
        if glazes:
            return glazes
        else:
            return None

class Image(db.Model):
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    name = db.Column(db.String(256))
    create_date = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    edit_date = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    delete_date = db.Column(db.DateTime, index=True)

    def __repr__(self):
        return 'Image {}'.format(self.name)


class ItemImage(db.Model):
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    image_id = db.Column(db.Integer, db.ForeignKey('image.id'))
    item_id = db.Column(db.Integer, db.ForeignKey('item.id'))
    order = db.Column(db.Integer)

    def delete_image(self):
        image_items_to_update = db.session.query(ItemImage).filter_by(item_id=self.item_id) \
            .filter(ItemImage.order > self.order).all()
        print(image_items_to_update)
        if len(image_items_to_update) > 0:
            for image_item in image_items_to_update:
                print(image_item)
                image_item.order -= 1
        db.session.delete(self)
        db.session.commit()

    def make_image_first(self):
        image_items_to_update = db.session.query(ItemImage).filter_by(item_id=self.item_id).filter(ItemImage.order < self.order).all()
        print(image_items_to_update)
        if len(image_items_to_update) > 0:
            for image_item in image_items_to_update:
                print(image_item)
                image_item.order += 1
        self.order = 0
        db.session.commit()


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    recovery_word = db.Column(db.String(64))
    recovery_date = db.Column(db.DateTime)

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def set_recovery_word(self):
        self.recovery_word = ''.join(random.choices(string.ascii_lowercase + string.digits, k=15))
        self.recovery_date = datetime.utcnow() + timedelta(days=1)
        return self.recovery_word

    def get_material_types(self):
        return MaterialType.query.order_by('id')

    def get_items(self):
        return Item.query.filter_by(user_id=self.id).filter(Item.delete_date == None).order_by(desc(Item.edit_date))

    def get_materials(self, type_id):
        return Material.query.filter_by(user_id=self.id).filter_by(type_id=type_id).filter(
            Material.delete_date == None).order_by('id')

    def get_global_materials(self, type_id):
        return Material.query.filter_by(type_id=type_id).filter(Material.delete_date == None).order_by('id')

    def get_all_materials(self):
        return Material.query.filter_by(user_id=self.id).filter(Material.delete_date == None).order_by(
            desc('edit_date'))

    def get_glazes(self):
        return self.get_all_materials().filter_by(type_id=1)

    @login.user_loader
    def load_user(id):
        return User.query.get(int(id))

# db.create_all()
