from datetime import datetime

from marshmallow import Schema, fields

from . import db, ma

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(50), unique=True, nullable=False)
    id_no = db.Column(db.Integer,  unique=True, nullable=False)
    full_name = db.Column(db.String(30), nullable=False)
    phone = db.Column(db.Integer,  unique=False, nullable=False)
    password = db.Column(db.String(80), nullable=False)
    # Upon suspension, this value shall be changed to 1 and upon restoration shall change to 2
    is_suspended = db.Column(db.Integer, default=0) 

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
    def fetch_by_id_no(cls, id_no):
        return cls.query.filter_by(id_no=id_no).first()

    @classmethod
    def fetch_by_email(cls, email):
        return cls.query.filter_by(email=email).first()

    @classmethod
    def fetch_by_username(cls, username):
        return cls.query.filter_by(username=username).first()

    @classmethod
    def fetch_by_full_name(cls, username):
        return cls.query.filter_by(full_name=full_name).first()

    @classmethod
    def suspend_user(cls, id, is_suspended=None):
        record = cls.fetch_by_id(id)
        if is_suspended:
            record.is_suspended = is_suspended
        db.session.commit()
        return True

    @classmethod
    def restore_user(cls, id, is_suspended=None):
        record = cls.fetch_by_id(id)
        if is_suspended:
            record.is_suspended = is_suspended
        db.session.commit()
        return True

    @classmethod  
    def update_user(cls, id, email=None, full_name=None, username=None):
        record = cls.fetch_by_id(id)
        if email:
            record.email = email
        if full_name:
            record.full_name = full_name
        if username:
            record.username = username
        db.session.commit()
        return True

    @classmethod  
    def update_password(cls, id, password=None):
        record = cls.fetch_by_id(id)
        if password:
            record.password = password
        db.session.commit()
        return True

    @classmethod
    def delete_by_id(cls, id):
        record = cls.query.filter_by(id=id)
        record.delete()
        db.session.commit()
        return True


class UserSchema(ma.ModelSchema):
    class Meta:
        fields = ('id','email','full_name', 'username', 'is_suspended', 'created', 'updated')
        #model = User
    """     
    email = fields.Email(required=True, error_messages={'required': {'message': 'Please enter a valid email address', 'code': 400}})
    full_name = fields.String(required=True, error_messages={'required': {'message': 'Full name required', 'code': 400}})
    username = fields.String(required=True, error_messages={'required': {'message': 'Username required', 'code': 400}})
    password = fields.String(required=True, error_messages={'required': {'message': 'Password required', 'code': 400}}) 
    """
    
""" 
class UserLoginSchema(ma.ModelSchema):
    email = fields.Email(required=True, error_messages={'required': {'message': 'Please enter a valid email address', 'code': 400}})
    password = fields.String(required=True, error_messages={'required': {'message': 'Password required', 'code': 400}})

class UserUpdateSchema(ma.ModelSchema):
    email = fields.Email(required=True, error_messages={'required': {'message': 'Please enter a valid email address', 'code': 400}})
    full_name = fields.String(required=True, error_messages={'required': {'message': 'Full name required', 'code': 400}})
    username = fields.String(required=True, error_messages={'required': {'message': 'Username required', 'code': 400}})
 """

