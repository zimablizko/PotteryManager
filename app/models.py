from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

from app import db

#Base = declarative_base()

class Item(db.Model):
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    name = db.Column(db.String(64), index=True, unique=True)
    clay_id_1 = db.Column(db.Integer, db.ForeignKey('clay.id'))
    clay_id_2 = db.Column(db.Integer, db.ForeignKey('clay.id'))
    picture = db.Column(db.String(256))

    def __repr__(self):
        return 'Item {}, {}'.format(self.name, self.picture)


class Clay(db.Model):
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    name = db.Column(db.String(64), index=True, unique=True)

    def __repr__(self):
        return 'Clay {}'.format(self.name)


#class ItemPicture(db.Model, Image):
#    item_id = db.Column(db.Integer, db.ForeignKey('item.id'), primary_key=True)
#    item = relationship('Item')