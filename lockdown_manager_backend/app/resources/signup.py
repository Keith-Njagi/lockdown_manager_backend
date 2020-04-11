from datetime import timedelta

from flask_restx import Namespace, Resource, fields
from werkzeug.security import generate_password_hash
from flask_jwt_extended import create_access_token, create_refresh_token
from flask import abort
from marshmallow import ValidationError


from models.user_model import User, UserSchema
from models.user_roles_model import UserRole, UserRoleSchema
from user_functions.user_role_manager import UserPrivilege

api = Namespace('signup', description='Sign up')

user_schema = UserSchema()
user_role_schema = UserRoleSchema()

user_model = api.model('SignUp', {
    'email': fields.String(required=True, description='Email'),
    'id_no': fields.Integer(required=True, description='id_no'),
    'full_name': fields.String(required=True, description='Full Name'),
    'country_code': fields.Integer(required=True, description='Country Code'),
    'phone': fields.Integer(required=True, description='phone'),
    'password': fields.String(required=True, description='Password')
})


@api.route('')
class Register(Resource):
    @api.expect(user_model)
    @api.doc('register_user')
    def post(self):
        '''Register User'''
        data = api.payload
        if not data:
            abort(400, 'No input data detected')

        email = data['email'].lower()
        user = User.fetch_by_email(email)
        if user:
            abort(400, 'Falied... A user with this email already exists')

        id_no = data['id_no']
        user = User.fetch_by_id_no(id_no)
        if user:
            abort(400, 'Falied... A user with this ID number already exists')

        full_name = data['full_name'].lower()
        hashed_password = generate_password_hash(data['password'], method='sha256')

        new_user = User(email=email, id_no=id_no, full_name=full_name,country_code=data['country_code'], phone=data['phone'], password=hashed_password)
        new_user.insert_record()

        user = user_schema.dump(data)

        this_user = User.fetch_by_email(email)

        UserPrivilege.generate_user_role(user_id = this_user.id)
        user_id = UserPrivilege.user_id
        role = UserPrivilege.role
        new_user_role = UserRole(user_id=user_id, role=role)
        new_user_role.insert_record()

        privileges =UserPrivilege.privileges
        expiry_time = timedelta(minutes=30)
        my_identity = {'id':this_user.id, 'privileges':privileges}
        access_token = create_access_token(identity=my_identity, expires_delta=expiry_time)
        refresh_token = create_refresh_token(my_identity)        
        return {'message': 'Success', 'access token': access_token, "refresh_token": refresh_token, 'user': user}, 201
