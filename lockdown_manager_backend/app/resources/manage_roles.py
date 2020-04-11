from datetime import timedelta

from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt_claims
from flask import abort
from werkzeug.exceptions import BadRequest
from marshmallow import ValidationError

from models.user_roles_model import UserRole, UserRoleSchema
from user_functions.user_role_manager import UserPrivilege

api = Namespace('roles', description='Update User')


user_role_schema = UserRoleSchema()
user_roles_schema = UserRoleSchema(many=True)

user_role_model = api.model('UpdateUserRole', {
    'role': fields.Integer(required=True, description='Role'),
})

@api.route('')
class UserRoleList(Resource):
    @api.doc('Get all user roles')
    @jwt_required
    def get(self):
        '''Get All User Roles'''
        claims = get_jwt_claims()
        if not claims['is_admin']:
            abort(400, 'You do not have the required permissions!')
        my_roles = UserRole.fetch_all()
        roles = user_roles_schema.dump(my_roles)
        return {'status':'Matches retrieved', 'roles':roles}, 200

@api.route('/<int:id>')
class UserRoleList(Resource):
    @api.doc('Update a user role')
    @api.expect(user_role_model)
    @jwt_required
    def put(self, id):
        '''Update a User Role'''
        claims = get_jwt_claims()
        if not claims['is_admin']:
            abort(400, 'You do not have the required permissions!')

        data = api.payload
        if not data:
            abort(400, 'No input data detected')

        role_record = UserRole.fetch_by_user_id(id)
        if role_record:
            role = data['role']
            id = role_record.id
            UserRole.update_role(id, role=role)
            user_role = user_role_schema.dump(role_record)
            return {'message': 'User role updated', 'role': user_role}
        return {'message': 'Record not found'}, 400