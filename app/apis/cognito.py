from botocore.errorfactory import ClientError
from flask import request
from flask_restx import Namespace, Resource, fields
from warrant import Cognito

from core.data import ReturnDocument
from settings import awsRegion, cognitoUserPoolId, cognitoUserPoolClientId

api = Namespace('cognito', description='AWS cognito services')


@api.route('/register/')
class RegisterUser(Resource):
    model = api.model(
        'RegisterUser',
        {'email': fields.String, 'name': fields.String, "family_name": fields.String, "password": fields.String},
    )

    @api.expect(model, validate=True)
    def post(self):
        """Get user details"""
        json_data = request.get_json(force=True)

        email = json_data['email']
        name = json_data['name']
        family_name = json_data['family_name']
        pwd = json_data['password']
        try:
            u = Cognito(cognitoUserPoolId, cognitoUserPoolClientId, awsRegion)
            u.add_base_attributes(name=name, family_name=family_name)
            u.register(email, password=pwd)

            return ReturnDocument(email, "success").asdict()
        except ClientError as err:
            return ReturnDocument(err.__str__(), "error").asdict()


@api.route('/register/confirm/')
class ConfirmUser(Resource):
    model = api.model(
        'ConfirmUser', {'email': fields.String, 'code': fields.String},
    )

    @api.expect(model, validate=True)
    def post(self):
        """Confirm user registration"""
        json_data = request.get_json(force=True)

        email = json_data['email']
        code = json_data['code']

        try:
            u = Cognito(cognitoUserPoolId, cognitoUserPoolClientId, awsRegion)
            u.confirm_sign_up(code, username=email)

            return ReturnDocument(email, "success").asdict()
        except ClientError as err:
            return ReturnDocument(err.__str__(), "error").asdict()


@api.route('/logout/')
class ConfirmUser(Resource):
    model = api.model(
        'LogoutUser', {
            'email': fields.String,
            "id_token": fields.String,
            "refresh_token": fields.String,
            "access_token": fields.String,
        },
    )

    @api.expect(model, validate=True)
    def post(self):
        """Logout user from all devices"""
        json_data = request.get_json(force=True)

        email = json_data['email']
        refresh_token = json_data['refresh_token']
        id_token = json_data['id_token']
        access_token = json_data['access_token']

        try:
            u = Cognito(cognitoUserPoolId, cognitoUserPoolClientId, awsRegion, id_token=id_token,
                        refresh_token=refresh_token, access_token=access_token)
            u.logout()

            return ReturnDocument(email, "success").asdict()
        except ClientError as err:
            return ReturnDocument(err.__str__(), "error").asdict()


@api.route('/login/forget/initiate/')
class InitiateForgetPassword(Resource):
    model = api.model(
        'InitiateForgetPassword', {'email': fields.String},
    )

    @api.expect(model, validate=True)
    def post(self):
        """Sends a verification code to the user to use to change their password."""
        json_data = request.get_json(force=True)
        print(json_data)
        email = json_data['email']

        try:
            u = Cognito(cognitoUserPoolId, cognitoUserPoolClientId, awsRegion, username=email)
            u.initiate_forgot_password()
            return ReturnDocument(email, "success").asdict()
        except ClientError as err:
            return ReturnDocument(err.__str__(), "error").asdict()


@api.route('/login/forget/')
class ForgetPassword(Resource):
    model = api.model(
        'ForgetPassword', {'email': fields.String, 'code': fields.String, "password": fields.String}
    )

    @api.expect(model, validate=False)
    def post(self):
        """Allows a user to enter a code provided when they reset their password to update their password."""
        json_data = request.get_json(force=True)
        print(f"Reset pwd code: {json_data}")
        email = json_data['email']
        code = json_data['code']
        password = json_data['password']
        try:
            u = Cognito(cognitoUserPoolId, cognitoUserPoolClientId, awsRegion, username=email)
            u.confirm_forgot_password(code, password=password)

            return ReturnDocument(email, "success").asdict()
        except ClientError as err:
            return ReturnDocument(err.__str__(), "error").asdict()


@api.route('/login/')
class LoginUser(Resource):
    model = api.model(
        'ForgetPassword', {'email': fields.String, 'code': fields.String},
    )

    @api.expect(model, validate=True)
    def post(self):
        """login/authenticate a user"""
        json_data = request.get_json(force=True)

        email = json_data['email']
        password = json_data['password']

        try:
            u = Cognito(cognitoUserPoolId, cognitoUserPoolClientId, awsRegion, username=email)
            u.authenticate(password)
            data = {
                # "email":email,
                "id_token": u.id_token,
                "refresh_token": u.refresh_token,
                "access_token": u.access_token,
                "token_type": u.token_type,
            }
            print(ReturnDocument(data, "success").asdict())
            return ReturnDocument(data, "success").asdict()
        except ClientError as err:
            return ReturnDocument(err.__str__(), "error").asdict()
