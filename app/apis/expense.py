from flask_restx import Namespace, Resource

from core.data import ReturnDocument
from db import Expense, RepositoryException
from db.factory import create_repository
from settings import REPOSITORY_NAME, REPOSITORY_SETTINGS

# Database
repository = create_repository(REPOSITORY_NAME, REPOSITORY_SETTINGS)

api = Namespace('expenses', description='For managing expenses')


@api.route('/add/<email>&<amount>')
@api.param('payor', 'Email ID of payor')
@api.param('comments', 'Additional comments')
@api.param('description', 'Description of expense')
@api.param('date', 'Date of expense')
@api.param('amount', 'Amount paid')
@api.param('email', 'Email ID of payee')
class AddExpense(Resource):
    """Add expense"""

    def post(self, email, amount, date=None, description=None, comments=None, payor=None):
        try:
            repository.get_user(email)
            exp: Expense = Expense(email, amount, date, description, comments, payor)
            repository.add_expense(exp)
            return ReturnDocument(exp.id, "success").asdict()

        except RepositoryException as err:
            return ReturnDocument(err.__doc__, "error").asdict()


@api.route('/<id>')
class GetExpense(Resource):
    """Get details of a particular expense"""

    def get(self, id):
        try:
            exp: Expense = repository.get_expense(id)
            return ReturnDocument(exp.to_dict(), "success").asdict()

        except RepositoryException as err:
            return ReturnDocument(err.__doc__, "error").asdict()
