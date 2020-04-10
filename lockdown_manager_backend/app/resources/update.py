from datetime import timedelta

from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask import abort
from werkzeug.exceptions import BadRequest
from marshmallow import ValidationError


from models.user_model import User, UserSchema

api = Namespace('update', description='Update User')

user_schema = UserSchema()
users_schema = UserSchema(many=True)

user_model = api.model('UpdateUser', {
    'email': fields.String(required=True, description='Email'),
    'id_no': fields.Integer(required=True, description='ID Number'),
    'full_name': fields.String(required=True, description='Full Name'),
    'phone': fields.Integer(required=True, description='Phone')
})

@api.route('/<int:id>')
@api.param('id', 'The user identifier')
class UpdateUser(Resource):
    @api.doc('update_user')
    @api.expect(user_model)
    @jwt_required
    def put(self,id):
        '''Update User'''
        my_user = User.fetch_by_id(id)
        user = user_schema.dump(my_user)
        if len(user) == 0:
            abort(400, 'User does not exist')

        authorised_user = get_jwt_identity()
        if id != authorised_user:
            abort(400, 'You cannot modify this user! Please log in as this user to modify.')# 403

        data = api.payload
        if not data:
            abort(400, 'No input data detected')

        email = data['email'].lower()

        db_user = User.fetch_by_email(email)
        user_to_check = user_schema.dump(db_user)
        if len(user_to_check) > 0:
            if email == user_to_check['email'] and id != user_to_check['id']:
                abort(400, 'Falied... A user with this email already exists')

        id_no = data['id_no']
        db_user = Userfetch_by_id_no(id_no)
        user_to_check = user_schema.dump(db_user)
        if len(user_to_check) > 0:
            if id_no == user_to_check['email'] and id != user_to_check['id']:
                abort(400, 'Falied... A user with this email already exists')

        full_name = data['full_name']
        phone = data['phone']

        User.update_user(id=id, email=email, id_no=id_no, full_name=full_name, phone=phone)

        this_user = User.fetch_by_id_no(id_no)
        current_user = user_schema.dump(this_user)

        return {'message': 'User updated', 'user': current_user}, 200
