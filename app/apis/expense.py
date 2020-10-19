from flask_restx import Namespace, Resource

api = Namespace('expenses', description='For managing expenses')


@api.route('/add/<email>&<amount>&<date>')
@api.param('payor', 'Email ID of payor')
@api.param('comments', 'Additional comments')
@api.param('description', 'Description of expense')
@api.param('date', 'Date of expense')
@api.param('amount', 'Amount paid')
@api.param('email', 'Email ID of payee')
class PostExpense(Resource):
    def post(self, email):
        return {'id': email}
