from datetime import datetime

from marshmallow import Schema, fields

from . import db, ma
from .user_model import User


class UserRole(db.Model):
    __tablename__ = 'user_roles'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=False)
    user = db.relationship('User', backref=db.backref("user_roles", single_parent=True, lazy=True))
    # 1 = Owner
    # 2 = Admin
    # 3 = Observer
    # 4 = User
    role = db.Column(db.Integer, nullable=False)
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
        return cls.query.filter_by(user_id=user_id).first()

class UserRoleSchema(ma.ModelSchema):
    class Meta:
        model = UserRole