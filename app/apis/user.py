from flask_restx import Namespace, Resource

api = Namespace('users', description='For managing users and friends')


@api.route('/search/<email>')
@api.param('email', 'Email ID of user')
class QueryUser(Resource):
    def get(self, email):
        return {'id': email}


@api.route('/add/<email>')
@api.param('email', 'Email ID of friend')
class QueryUser(Resource):
    def post(self, email):
        return {'id': email}
