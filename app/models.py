from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

from app import db


# =Base = declarative_base()

class Clay(db.Model):
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    name = db.Column(db.String(64), index=True, unique=True)

    def __repr__(self):
        return 'Clay {}'.format(self.name)


class Glaze(db.Model):
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    name = db.Column(db.String(64), index=True, unique=True)

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
    name = db.Column(db.String(64))
    description = db.Column(db.Text(512))
    clay_id = db.Column(db.Integer, db.ForeignKey('clay.id'))
    surface_id = db.Column(db.Integer, db.ForeignKey('surface.id'))
    temperature = db.Column(db.Integer)
    image_name = db.Column(db.String(256))

    def __repr__(self):
        return 'Item {}, {}'.format(self.name, self.image_name)

# db.create_all()
