from flask import make_response
from flask_restx import Api

from core.transformer import XmlTransformer
from .cognito import api as cognito
from .expense import api as expense
from .user import api as user

api = Api(
    version="0.1",
    title="Greevil",
    description="APIs For Money Management, Expense Tracking, Financial Tools and User Management"
)


@api.representation('application/xml')
def xml(data, code, headers):
    resp = make_response(str(XmlTransformer(data)), code)
    resp.headers.extend(headers)
    return resp


api.add_namespace(user)
api.add_namespace(expense)
api.add_namespace(cognito)
