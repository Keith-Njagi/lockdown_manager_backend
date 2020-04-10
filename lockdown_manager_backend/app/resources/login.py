from datetime import timedelta

from flask import abort
from flask_restx import Namespace, Resource, fields
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_refresh_token_required
from marshmallow import ValidationError

from models.user_model import User, UserSchema


api = Namespace('login', description='Log in')

user_schema = UserSchema()
users_schema = UserSchema(many=True)

my_user_model = api.model('Login', {
    'id_no': fields.Integer(required=True, description='ID Number'),
    'password': fields.String(required=True, description='Password')

})


@api.route('')
class Login(Resource):
    @api.doc('login_user')
    @api.expect(my_user_model)
    def post(self):
        '''Log in user'''
        data = api.payload
        if not data:
            abort(400, 'No input data detected')

        id_no = data['id_no']
        this_user = User.fetch_by_id_no(id_no)
        print(this_user)
        if this_user:
            if check_password_hash(this_user.password, data['password']):
                current_user = user_schema.dump(this_user)
                expiry_time = timedelta(minutes=30)
                access_token = create_access_token(identity=this_user.id, expires_delta=expiry_time)
                refresh_token = create_refresh_token(this_user.id)
                return {'message': 'User logged in', 'user': current_user, 'access_token': access_token, "refresh_token": refresh_token}, 200
        if not this_user or not check_password_hash(user.password, data['password']):
            return {'message': 'Could not log in, please check your credentials'}, 400

# @api.route('/mail')
# class MailLogin(Resource):
#     @api.doc('login_from_mail')
#     def get(self):
#         '''Log in from mail link'''
#         pass

@api.route('/refresh')
class TokenRefresh(Resource):
    @jwt_refresh_token_required
    @api.doc('reset_token')
    def post(self):
        '''Reset JWT Token'''
        current_user = get_jwt_identity()
        new_token = create_access_token(identity=current_user, fresh=False)
        return {"access_token": new_token}, 200
