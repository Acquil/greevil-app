from datetime import datetime

import pandas as pd
from botocore.exceptions import ClientError
from flask import request
from flask_restx import Namespace, Resource, fields

from core.data import ReturnDocument
from db import Expense, RepositoryException, User
from db.factory import create_repository
from settings import REPOSITORY_NAME, REPOSITORY_SETTINGS

# Database
repository = create_repository(REPOSITORY_NAME, REPOSITORY_SETTINGS)

api = Namespace('expenses', description='For managing expenses')

expense_fields = api.model(
    'AddExpense', {
        'email': fields.String(description="Email ID of payee", required=True),
        'amount': fields.String(description="Description of expense", required=True, min=1),
        'date': fields.Date(description='Date of expense in ISO format(yy-mm-dd)'),
        'description': fields.String(description='Description of expense'),
        'comments': fields.String(description='Additional comments'),
        "payor": fields.String(description='Email ID of payor'),
    },
)


@api.route('/add/')
class AddExpense(Resource):

    @api.expect(expense_fields, validate=False)
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

            exp: Expense = Expense(user_id=email, amount=amount, date=date, description=description, comments=comments,
                                   payor=payor)
            repository.add_expense(exp)

            return ReturnDocument(exp.id, "success").asdict()

        except RepositoryException as err:
            return ReturnDocument(err.__doc__, "error").asdict()
        except KeyError as err:
            return ReturnDocument(f"{err.__str__()}-{err.__doc__}", "error").asdict()
        except ValueError as err:
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


@api.route('/stats/')
class ExpenseStats(Resource):
    model = api.model(
        "GetStats", {
            'email': fields.String(description="User email ID", required=True),
        }
    )

    @api.expect(model)
    def post(self):
        exp_list = []
        data = request.get_json(force=True)
        email_id = data['email']

        try:
            usr: User = repository.get_user(email_id)
            for exp in usr.expense_ids:
                exp_obj: Expense = repository.get_expense(exp)
                exp_list.append(exp_obj.to_dict())
            if not exp_list:
                data = {
                    "exp_list": [],
                    "area_chart": {},
                    "bar_chart": {},
                    "pie_chart": {},
                    "new_expenses": 0,
                    "monthly_expenses": 0,
                    "friends_amount": 0,
                    "owed_amount": 0
                }
            else:
                df = pd.DataFrame(exp_list).sort_values('date')

                df['amount'] = pd.to_numeric(df['amount'])
                df['month'] = pd.to_numeric(df["date"].apply(lambda x: x[5:7]))
                df['year'] = pd.to_numeric(df["date"].apply(lambda x: x[0:4]))
                df['day'] = pd.to_numeric(df["date"].apply(lambda x: x[8:10]))

                now = datetime.now()
                area_chart = df[df['year'] == now.year].groupby(['date'])['amount'].sum()
                bar_chart = df.groupby(['month'])['amount'].sum()

                new_expenses = df[(df['year'] == now.year) & (df['month'] == now.month) & (df['day'] == now.day)][
                    'amount'].sum()
                monthly_expenses = df[(df['year'] == now.year) & (df['month'] == now.month)]['amount'].sum()

                friends_amount = df[(df['payor'] != email_id) & (df['user_id'] == email_id)]['amount'].sum()
                owed_amount = df[('payor' == email_id) & (df['user_id'] != email_id)]['amount'].sum()

                pie_chart = df[(df['payor'] != email_id) & (df['user_id'] == email_id)].groupby(['payor'])['amount'].sum()

                data = {
                    "exp_list": exp_list,
                    "area_chart": area_chart.to_dict(),
                    "bar_chart": bar_chart.to_dict(),
                    "pie_chart": pie_chart.to_dict(),
                    "new_expenses": new_expenses,
                    "monthly_expenses": monthly_expenses,
                    "friends_amount": friends_amount,
                    "owed_amount": owed_amount
                }

            return ReturnDocument(data, "success").asdict()
        except RepositoryException as err:
            return ReturnDocument(err.__doc__, "error").asdict()
        except ClientError as err:
            return ReturnDocument(err.__str__(), "error").asdict()
