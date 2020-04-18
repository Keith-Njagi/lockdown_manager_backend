from datetime import datetime, timedelta

from flask import abort
from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt_claims
from marshmallow import ValidationError

from models.permits_model import OutdoorPermit, OutdoorPermitSchema

api = Namespace('permit', description='Log in')

permit_schema = OutdoorPermitSchema()
permits_schema = OutdoorPermitSchema(many=True)

permits_model = api.model('OutdoorPermit', {
    'current_location': fields.String(required=True, description='Current Location'),
    'destination': fields.String(required=True, description='Destination'),
    'time_from': fields.DateTime(required=True, description='Time From'),
    'time_to': fields.DateTime(required=True, description='Time To')
})

@api.route('')
class OutdoorPermits(Resource):
    @api.doc('list_permits')
    @jwt_required
    def get(self, id):
        '''Get all Permits'''
        all_permits = OutdoorPermit.fetch_all()
        if all_permits:
            permits = permits_schema.dump(all_permits)
            return {'permits': permits}, 200
        return {'error': 'Unable to retrieve matches'}, 400

@api.route('/user/<int:id>')
@api.param('id', 'The user identifier')
class PermitList(Resource):
    @api.doc('list_user_permits')
    @jwt_required
    def get(self, id):
        '''Get all User Permits'''
        user_permits = OutdoorPermit.fetch_by_user_id(user_id=id)
        if user_permits:
            permits = permits_schema.dump(user_permits)
            return {'permits': permits}, 200
        return {'error': 'Unable to retrieve matches'}, 400

    @api.doc('submit_user_permit')
    @api.expect(permits_model)
    @jwt_required
    def post(self, id):
        '''Post Permit'''
        authorised_user = get_jwt_identity()
        if id != authorised_user['id']:
            abort(400, 'You cannot modify this user! Please log in as this user to modify.')

        data = api.payload
        if not data:
            abort(400, 'No input data detected')

        user_id = id
        current_location = data['current_location']
        destination = data['destination']
        time_from = data['time_from'] # datetime.utcnow()
        time_to = data['time_to'] # datetime.utcnow()+timedelta(hours=1)

        try:
            new_permit = OutdoorPermit(user_id=user_id, current_location=current_location, destination=destination, time_from=time_from, time_to=time_to)
            new_permit.insert_record()
            return {'message': 'Success', 'permit': data}, 200
        except Exception as e:
            return {'message': 'Unable to insert this record.', 'error': e}, 200



@api.route('/permit/<int:id>')
@api.param('id', 'The permit identifier')
class Permit(Resource):
    @api.doc('list_user_permits')
    @jwt_required
    def get(self, id):
        '''Get User Permit'''
        this_permit = OutdoorPermit.fetch_by_id(id)
        if this_permit:
            authorised_user = get_jwt_identity()
            claims = get_jwt_claims()
            if this_permit.id != authorised_user['id'] or authorised_user['role'] != 'observer' or claims['is_admin'] == False:
                abort(400, 'You are not authorised to access this permit!')

            permit = permit_schema.dump(this_permit)
            return {'permit': permit}, 200
        return {'message': 'Permit does not exist'}, 400

