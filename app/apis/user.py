from flask_restx import Namespace, Resource

from db import User
from db.factory import create_repository
from settings import REPOSITORY_NAME, REPOSITORY_SETTINGS

# Database
repository = create_repository(REPOSITORY_NAME, REPOSITORY_SETTINGS)

api = Namespace('users', description='For managing users and friends')


@api.route('/search/<email>')
@api.param('email', 'Email ID of user')
class QueryUser(Resource):
    def get(self, email):
        user: User = repository.get_user(email)
        # return {'id': user.id}
        return user.to_dict()


@api.route('/<email>&<name>')
@api.param('email', 'Email ID of user')
@api.param('name', 'Name of user')
class AddUser(Resource):
    def post(self, email, name):
        repository.add_user(User(id=email, name=name))
        return {'status': "done"}


@api.route('/add/<id>&<fid>')
@api.param('id', 'ID of user')
@api.param('fid', 'Email ID of friend')
class AddFriend(Resource):
    def post(self, id, fid):
        repository.add_friend(user_id=id, friend_id=fid)
        return {
            'user': id,
            'friend': fid,
            'status': "done"
        }
