import time

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
add_friend_fields = api.model(
    'AddFriend', {'your_id': fields.String, 'friend_id': fields.String},
)
filtered_expense_fields = api.model(
    'UserExpenses', {'email': fields.String, 'from_date': fields.Date, 'to_date': fields.Date, }
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
    parser = reqparse.RequestParser()
    parser.add_argument('email', type=str)

    @api.expect(query_user_fields)
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
    # parser.add_argument('User-Agent', location='values')
    parser.add_argument('last_name', type=str)
    parser.add_argument('first_name', type=str)
    parser.add_argument('personal_data', type=dict)

    def get(self):
        xml_data = xmltodict.parse(request.get_data())
        return dict(xml_data)


@api.route('/add/')
class AddUser(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('email', type=str)
    parser.add_argument('name', type=str)

    @api.expect(add_user_fields)
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


@api.route('/add/friend/')
class AddFriend(Resource):
    """Add friend"""
    parser = reqparse.RequestParser()
    parser.add_argument('your_id', type=str)
    parser.add_argument('friend_id', type=str)

    @api.expect(add_friend_fields)
    def post(self):
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

    @api.expect(filtered_expense_fields)
    def post(self):
        """
        Get all expenses of a particular user
        """
        parser = reqparse.RequestParser()
        parser.add_argument('your_id', type=str)
        parser.add_argument('friend_id', type=str)

        data = request.get_json(force=True)
        email_id = data['email']
        from_date = data['from_date']
        from_date = time.strptime(from_date, "%d/%m/%Y")
        to_date = data['to_date']
        to_date = time.strptime(to_date, "%d/%m/%Y")

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
