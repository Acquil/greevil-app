from flask import request
from flask_restx import Namespace, Resource, fields

from core.data import ReturnDocument
from db import Expense, RepositoryException
from db.factory import create_repository
from settings import REPOSITORY_NAME, REPOSITORY_SETTINGS

# Database
repository = create_repository(REPOSITORY_NAME, REPOSITORY_SETTINGS)

api = Namespace('expenses', description='For managing expenses')

expense_fields = api.model(
    'AddExpense', {
        'email': fields.String(description="Email ID of payee", required=True),
        'amount': fields.Float(description="Description of expense", required=True, min=0),
        'date': fields.Date(description='Date of expense in ISO format(yy-mm-dd)'),
        'description': fields.String(description='Description of expense'),
        'comments': fields.String(description='Additional comments'),
        "payor": fields.String(description='Email ID of payor'),
    },
)


@api.route('/add/')
class AddExpense(Resource):

    @api.expect(expense_fields, validate=True)
    def post(self):
        """
        Add expense
        """
        try:
            data = request.get_json(force=True)
            email = data['email']
            amount = data['amount']
            date = data['date']
            description = data['description']
            comments = data['comments']
            payor = data['payor']

            repository.get_user(email)
            exp: Expense = Expense(email, amount, date, description, comments, payor)
            repository.add_expense(exp)
            return ReturnDocument(exp.id, "success").asdict()

        except RepositoryException as err:
            return ReturnDocument(err.__doc__, "error").asdict()
        except KeyError or ValueError as err:
            return ReturnDocument(f"{err.__str__()}-{err.__doc__}", "error").asdict()


@api.route('/delete/')
class DeleteExpense(Resource):
    model = api.model(
        "DeleteExpense", {
            "id": fields.String(description="Expense to be deleted")
        }
    )

    @api.expect(model, validate=True)
    def post(self):
        """
        Delete expense
        """
        try:
            data = request.get_json(force=True)
            id = data['id']
            repository.delete_expense(id)
            return ReturnDocument(id, "success").asdict()
        except RepositoryException as err:
            return ReturnDocument(err.__doc__, "error").asdict()
        except KeyError or ValueError as err:
            return ReturnDocument(f"{err.__str__()}-{err.__doc__}", "error").asdict()


@api.route('/')
class GetExpense(Resource):
    model = api.model(
        "GetExpense", {"id": fields.String()}
    )

    @api.expect(model)
    def post(self):
        """Get details of a particular expense"""
        try:
            data = request.get_json()
            id = data['id']
            exp: Expense = repository.get_expense(id)
            return ReturnDocument(exp.to_dict(), "success").asdict()

        except RepositoryException as err:
            return ReturnDocument(err.__doc__, "error").asdict()
        except KeyError or ValueError as err:
            return ReturnDocument(f"{err.__str__()}-{err.__doc__}", "error").asdict()
