from datetime import timedelta

from flask import abort
from flask_restx import Namespace, Resource, fields
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token, jwt_required, get_raw_jwt, get_jwt_identity
from marshmallow import ValidationError

from models.user_model import User, UserSchema
from blacklist import BLACKLIST

api = Namespace('logout', description='Log out')

user_schema = UserSchema()
users_schema = UserSchema(many=True)


@api.route('')
class Logout(Resource):
    @api.doc('logout_user')
    @jwt_required
    def post(self):
        '''Log out user'''
        # jti is "JWT ID", a unique identifier for a JWT.
        jti = get_raw_jwt()["jti"]
        user_id = get_jwt_identity()
        BLACKLIST.add(jti)
        return {"message": f"User <id={user_id}> successfully logged out."}, 200
