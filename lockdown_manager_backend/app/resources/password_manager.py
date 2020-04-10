import base64
from datetime import timedelta, datetime
import smtplib
from email.mime.text import MIMEText

from flask_restx import Namespace, Resource, fields
from werkzeug.security import generate_password_hash
from flask_jwt_extended import create_access_token, create_refresh_token
from flask import abort
import uuid
from flask_mail import Message
from flask import render_template
import requests
from flask_mail import Mail, Message


#from . import mail
from models.user_model import User, UserSchema
from models.change_password_model import ChangePasswordToken, ChangePasswordTokenSchema
from user_functions.password_reset import PasswordReset#generate_reset_token, decode_reset_token


mail = Mail()


password_token_schema = ChangePasswordTokenSchema()
password_tokens_schema = ChangePasswordTokenSchema(many=True)
user_schema = UserSchema()
users_schema = UserSchema(many=True)


api = Namespace('password', description='Change User Password')

reset_token_model = api.model('PasswordResetToken', {
    'email': fields.String(required=True, description='Email registered under one of the accounts')
})

change_password_model = api.model('ChangePassword', {
    'password': fields.String(required=True, description='New Password')
})


@api.route('/forgot')
class SendResetLink(Resource):
    @api.doc('create_reset_link')
    @api.expect(reset_token_model)
    def post(self):
        '''Send email with password reset link'''
        data = api.payload

        if not data:
            abort(400, 'No input data detected')

        email = data['email'].lower()
        db_user = User.query.filter_by(email=email).first()
        user_to_check = user_schema.dump(db_user)
        if len( user_to_check) == 0:
            abort(400, 'Failed! Please use the email used to register your account')

        password_reset = PasswordReset()
        reset_code =password_reset.reset_code
        reset_token = password_reset.reset_token
        
        print(reset_token)

        user_id = db_user.id
        password_reset_record = ChangePasswordToken(user_id=user_id, email=email, reset_code=reset_code)
        password_reset_record.insert_record()

        # Write code to send link to email
        # Add a html to send along with the email containing a button that redirects to the password reset page
        template = render_template('password_reset.html', reset_token=reset_token)
        subject = "Password Reset"
        msg = Message('Hello', recipients=[email])#, sender = 'keithgatana@gmail.com'
        msg.body = 'We have noticed you have requested for a password change. Please click on the link belowZipFile The class for reading and writing ZIP files.  See section '
        msg.html = template
        # requests.post(
        #     "https://api.mailgun.net/v3/sandboxf470d9c93fd546539dac19fbe4f11c3c.mailgun.org/messages",
        #     auth=("api", "911f71e177b4b2477c6bf6a45af0af1e-f8faf5ef-677d72cb"),
        #     data={"from": "Excited User <mailgun@sandboxf470d9c93fd546539dac19fbe4f11c3c.mailgun.org>",
        #           "to": [email, "Ticko@sandboxf470d9c93fd546539dac19fbe4f11c3c.mailgun.org"],
        #           "subject": "Password Reset",
        #           "text": template})
        
        try:
            mail.send(msg)
            return {'message':'Success', 'reset_token':reset_token}, 200
        except Exception as e:
            print('description: ', e)
            return {'message': 'Couldn\'t send mail'}, 400

@api.route('/token/validity/<string:reset_token>')
class CheckTokenValidity(Resource):
    @api.doc('check_reset_password_token_validity')
    def get(self, reset_token):
        '''Verify Password Reset Token'''
        received_reset_token = reset_token
        PasswordReset.decode_reset_token(received_reset_token)
        token = PasswordReset.token

        # Check for an existing reset_token with is_expired status as False
        reset_code_record = ChangePasswordToken.fetch_by_reset_code(reset_code=token)
        if not reset_code_record:
            abort(400, 'Rejected! This reset token does not exist')

        set_to_expire = reset_code_record.created + timedelta(minutes=30)
        current_time = datetime.utcnow()
        if set_to_expire <= current_time:
            user_id = reset_code_record.user_id
            is_expired = True
            user_records = ChangePasswordToken.fetch_all_by_user_id(user_id)
            record_ids = []
            for record in user_records:
                record_ids.append(record.id)
            for record_id in record_ids:
                ChangePasswordToken.expire_token(id=record_id, is_expired=is_expired)
            abort(400, 'Rejected! Password reset token is expired. Please request a new password reset.')

        if reset_code_record.is_expired == True:
            user_id = reset_code_record.user_id
            is_expired = True
            user_records = ChangePasswordToken.fetch_all_by_user_id(user_id)
            record_ids = []
            for record in user_records:
                record_ids.append(record.id)
            for record_id in record_ids:
                ChangePasswordToken.expire_token(id=record_id, is_expired=is_expired)
            abort(400, 'Rejected! Password reset token has already been used. Please request a new password reset.')
        return {'message': 'Password reset token is active. You may type in your new password.'}, 200

@api.route('/reset/<string:reset_token>')
class ResetPassword(Resource):
    @api.doc('reset_password')
    @api.expect(change_password_model)
    def put(self, reset_token):
        '''Reset User Password'''
        received_reset_token = reset_token
        PasswordReset.decode_reset_token(received_reset_token)
        token = PasswordReset.token

        # Check for an existing reset_token with is_expired status as False
        reset_code_record = ChangePasswordToken.fetch_by_reset_code(reset_code=token)
        if not reset_code_record:
            abort(400, 'This reset token does not exist')
        
        if reset_code_record.is_expired == True:
            user_id = reset_code_record.user_id
            is_expired = True
            user_records = ChangePasswordToken.fetch_all_by_user_id(user_id)
            record_ids = []
            for record in record_ids:
                record_ids.append(record.id)
            for record_id in record_ids:
                ChangePasswordToken.expire_token(id=record_id, is_expired=is_expired)
            abort(400, 'Password reset token has already been used. Please request a new password reset.')

        user_id = reset_code_record.user_id
        is_expired = True
        user_records = ChangePasswordToken.fetch_all_by_user_id(user_id)
        record_ids = []
        for record in user_records:
            record_ids.append(record.id)
        for record_id in record_ids:
            ChangePasswordToken.expire_token(id=record_id, is_expired=is_expired)

        data = api.payload

        if not data:
            abort(400, 'No input data detected')

        password = data['password']
        hashed_password = generate_password_hash(data['password'], method='sha256')
        User.update_password(id=user_id, password=hashed_password)
        this_user = User.fetch_by_id(id=user_id)
        user = user_schema.dump(this_user)
        expiry_time = timedelta(minutes=30)
        access_token = create_access_token(identity=this_user.id, expires_delta=expiry_time)
        refresh_token = create_refresh_token(this_user.id)
        status = {'message': 'Successfully changed Password', 'access token': access_token, 'refresh token': refresh_token, 'user': user}
        return status, 200
