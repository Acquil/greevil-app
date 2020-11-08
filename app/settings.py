"""
Settings for the application.

You can set values of REPOSITORY_NAME and REPOSITORY_SETTINGS in
environment variables, or set the default values in code here.
"""

from os import environ

cognitoUserPoolId = "us-east-1_N3LQnEiUA"
cognitoUserPoolClientId = "2ar481vjkra0k54fu6c6vre6m0"
awsRegion = 'us-east-1'

# default storage
REPOSITORY_NAME = environ.get('REPOSITORY_NAME', 'dynamodb')

if REPOSITORY_NAME == 'memory':
    REPOSITORY_SETTINGS = {}

elif REPOSITORY_NAME == 'dynamodb':
    REPOSITORY_SETTINGS = {
        "DYNAMODB_USER_TABLE": environ.get('DYNAMODB_USER_TABLE', 'greevil-users'),
        "DYNAMODB_EXPENSE_TABLE": environ.get('DYNAMODB_EXPENSE_TABLE', 'greevil-expenses')
    }

else:
    raise ValueError('Unknown repository.')
