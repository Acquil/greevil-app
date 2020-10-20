from flask_restx import Namespace, Resource

from core.data import ReturnDocument
from db import User, RepositoryException
from db.factory import create_repository
from settings import REPOSITORY_NAME, REPOSITORY_SETTINGS

# Database
repository = create_repository(REPOSITORY_NAME, REPOSITORY_SETTINGS)

api = Namespace('users', description='For managing users and friends')


@api.route('/search/<email>')
@api.param('email', 'Email ID of user')
class QueryUser(Resource):
    """Get user"""

    def get(self, email):
        try:
            user: User = repository.get_user(email)
            return ReturnDocument(user.to_dict(), "success").asdict()
        except RepositoryException as err:
            return ReturnDocument(err.__doc__, "error").asdict()


@api.route('/<email>&<name>')
@api.param('email', 'Email ID of user')
@api.param('name', 'Name of user')
class AddUser(Resource):
    def post(self, email, name):
        """Add user"""
        try:
            repository.add_user(User(id=email, name=name))
            return {'status': "done"}
        except RepositoryException as err:
            return ReturnDocument(err.__doc__, "error").asdict()


@api.route('/add/<id>&<fid>')
@api.param('id', 'ID of user')
@api.param('fid', 'Email ID of friend')
class AddFriend(Resource):
    """Add friend"""

    def post(self, id, fid):
        try:
            repository.add_friend(user_id=id, friend_id=fid)
            return ReturnDocument(fid, "success").asdict()
        except RepositoryException as err:
            return ReturnDocument(err.__doc__, "error").asdict()


@api.route("/expenses/<id>")
@api.param("id", "ID of user")
@api.param("from_date", "ID of user")
@api.param("to_date", "ID of user")
class GetUserExpenses(Resource):

    def get(self, id, from_date=None, to_date=None):
        """
        Get all expenses of a particular user
        """
        # TODO date filter
        result = []
        try:
            usr: User = repository.get_user(id)
            for exp in usr.expense_ids:
                result.append(repository.get_expense(exp).to_dict())
            return ReturnDocument(result, "success").asdict()

        except RepositoryException as err:
            return ReturnDocument(err.__doc__, "error").asdict()
