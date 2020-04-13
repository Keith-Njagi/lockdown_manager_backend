from datetime import datetime, timedelta

from marshmallow import Schema, fields

from . import db, ma
from .user_model import User


class OutdoorPermit(db.Model):
    __tablename__ = 'outdoor_permits'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=False)
    user = db.relationship('User', backref=db.backref("outdoor_permits", single_parent=True, lazy=True))

    current_location = db.Column(db.String, nullable=False)
    destination = db.Column(db.String, nullable=False)

    time_from =  db.Column(db.DateTime, default=datetime.utcnow(), nullable=False)
    time_to = db.Column(db.DateTime, default=datetime.utcnow()+timedelta(hours=1) , nullable=False)

    created = db.Column(db.DateTime, default=datetime.utcnow(), nullable=False)
    updated = db.Column(db.DateTime, onupdate=datetime.utcnow(), nullable=True)

    def insert_record(self):
        db.session.add(self)
        db.session.commit()
        return self

    @classmethod
    def fetch_all(cls):
        return cls.query.order_by(cls.id.desc()).all()

    @classmethod
    def fetch_by_id(cls, id):
        return cls.query.filter_by(id=id).first()

    @classmethod
    def fetch_by_user_id(cls, user_id):
        return cls.query.filter_by(user_id=user_id).order_by(cls.id.desc()).all()



class OutdoorPermitSchema(ma.ModelSchema):
    class Meta:
        model = OutdoorPermit