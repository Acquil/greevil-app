import time
from datetime import datetime

import xmltodict
from flask import request
from flask_restx import Namespace, Resource, fields
from flask_restx import reqparse

from core.data import ReturnDocument
from db import User, RepositoryException, Expense
from db.factory import create_repository
from settings import REPOSITORY_NAME, REPOSITORY_SETTINGS

# Database
repository = create_repository(REPOSITORY_NAME, REPOSITORY_SETTINGS)

api = Namespace('user', description='For managing users and friends')

query_user_fields = api.model(
    'QueryUser', {'email': fields.String, },
)
add_user_fields = api.model(
    'AddUser', {'email': fields.String, 'name': fields.String},
)


@api.route('/search/<email>')
@api.param('email', 'Email ID of user')
class QueryUser(Resource):

    def get(self, email):
        """Get non-sensitive user information"""
        try:
            user: User = repository.get_user(email)
            data = {"email": user.id, "name": user.name}
            return ReturnDocument(data, "success").asdict()
        except RepositoryException as err:
            return ReturnDocument(err.__doc__, "error").asdict()


@api.route('/search/')
class QueryUserJson(Resource):

    @api.expect(query_user_fields, validate=True)
    def post(self):
        """Get user by email-id"""
        json_data = request.get_json(force=True)
        email = json_data['email']
        try:
            user: User = repository.get_user(email)
            return ReturnDocument(user.to_dict(), "success").asdict()
        except RepositoryException as err:
            return ReturnDocument(err.__doc__, "error").asdict()


@api.route('/search/xml/', doc=False)
class QueryUserXml(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('Content-Type', required=False, default='application/xml', location="headers")
    parser.add_argument('last_name', type=str, location="form")
    parser.add_argument('first_name', type=str)

    # parser.add_argument('personal_data', type=dict, location="json", help="Personal Data")
    @api.expect(parser)
    def post(self):
        xml_data = xmltodict.parse(request.get_data())
        return dict(xml_data)


@api.route('/add/')
class AddUser(Resource):

    @api.expect(add_user_fields, validate=True)
    def post(self):
        """Add user"""
        json_data = request.get_json(force=True)
        name = json_data['name']
        email = json_data['email']
        try:
            repository.add_user(User(id=email, name=name))
            return {'status': "done"}
        except RepositoryException as err:
            return ReturnDocument(err.__doc__, "error").asdict()
        except KeyError as err:
            return ReturnDocument(f"{err.__str__()}-{err.__doc__}", "error").asdict()


@api.route('/add/friend/')
class AddFriend(Resource):
    add_friend_fields = api.model(
        'AddFriend', {
            'your_id': fields.String(description="User email ID", required=True),
            'friend_id': fields.String(description="Email ID of friend", required=True)
        },
    )

    @api.expect(add_friend_fields, validate=True)
    def post(self):
        """
        Add friend
        """
        json_data = request.get_json(force=True)
        id = json_data['your_id']
        fid = json_data['friend_id']
        try:
            repository.add_friend(user_id=id, friend_id=fid)
            return ReturnDocument(fid, "success").asdict()
        except RepositoryException as err:
            return ReturnDocument(err.__doc__, "error").asdict()


@api.route("/view/expenses/")
class GetUserExpenses(Resource):
    filtered_expense_fields = api.model(
        'UserExpenses', {
            'email': fields.String(description="User email ID", required=True),
            'from_date': fields.Date(description="For filtering"),
            'to_date': fields.Date(description="For filtering"),
        },
    )

    @api.expect(filtered_expense_fields, validate=True)
    def post(self):
        """
        Get all expenses of a particular user
        """
        data = request.get_json(force=True)
        email_id = data['email']
        from_date = data.get('from_date')
        to_date = data.get('to_date')

        if from_date is None:
            from_date = datetime(1970, 1, 1)
        elif to_date is None:
            to_date = datetime.utcnow()
        else:
            from_date = time.strptime(from_date, "%Y-%m-%d")
            to_date = time.strptime(to_date, "%Y-%m-%d")

        result = []
        try:
            usr: User = repository.get_user(email_id)
            for exp in usr.expense_ids:
                exp_obj: Expense = repository.get_expense(exp)
                # Filter date
                if from_date < exp_obj.date < to_date:
                    result.append(exp_obj.to_dict())
            return ReturnDocument(result, "success").asdict()

        except RepositoryException as err:
            return ReturnDocument(err.__doc__, "error").asdict()
