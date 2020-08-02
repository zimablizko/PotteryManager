import random
import string
from datetime import datetime, timedelta

from flask_login import UserMixin
from sqlalchemy import desc
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from werkzeug.security import generate_password_hash, check_password_hash

from app import db, login


# =Base = declarative_base()

class Clay(db.Model):
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    name = db.Column(db.String(64))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    create_date = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    delete_date = db.Column(db.DateTime, index=True)

    def __repr__(self):
        return 'Clay {}'.format(self.name)


class Glaze(db.Model):
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    name = db.Column(db.String(64))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    create_date = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    delete_date = db.Column(db.DateTime, index=True)

    def __repr__(self):
        return 'Glaze {}'.format(self.name)


class Surface(db.Model):
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    name = db.Column(db.String(64), index=True, unique=True)

    def __repr__(self):
        return 'Surface {}'.format(self.name)


class ItemGlaze(db.Model):
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    glaze_id = db.Column(db.Integer, db.ForeignKey('glaze.id'))
    item_id = db.Column(db.Integer, db.ForeignKey('item.id'))
    order = db.Column(db.Integer)


class Item(db.Model):
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    name = db.Column(db.String(256))
    description = db.Column(db.Text(512))
    clay_id = db.Column(db.Integer, db.ForeignKey('clay.id'))
    surface_id = db.Column(db.Integer, db.ForeignKey('surface.id'))
    temperature = db.Column(db.Integer)
    image_name = db.Column(db.String(256))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    create_date = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    delete_date = db.Column(db.DateTime, index=True)
    is_public = db.Column(db.Boolean)

    def __repr__(self):
        return 'Item {}, {}'.format(self.name, self.image_name)

    def get_author(self):
        return User.query.filter_by(id=self.user_id).first()


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

    def get_surfaces(self):
        return Surface.query.order_by('id')

    def get_items(self):
        return Item.query.filter_by(user_id=self.id).filter(Item.delete_date == None).order_by(desc('id'))

    def get_materials(self, table):
        return table.query.filter_by(user_id=self.id).order_by('id')

    @login.user_loader
    def load_user(id):
        return User.query.get(int(id))

# db.create_all()
