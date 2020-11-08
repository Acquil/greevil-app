"""
Repository of users and expenses - dynamodb
"""

import boto3

from . import User, Expense, ExpenseNotFound, UserNotFound, UserExists


class Repository(object):
    """
    Dynamodb repository
    user table = greevil-users
        schema - CustomerId, Name, Expenses, Friends
    expenses table = greevil-expenses
        schema - ExpenseId, Amount, Date, Description, Comments, For, By
    """

    # TODO get all settings from settings.py
    def __init__(self, settings):
        """Initializes the repository. Note that settings are not used."""
        self.name = 'DynamoDB'

        self.dynamodb = boto3.resource('dynamodb', region_name="us-east-1")

        self.user_index = self.dynamodb.Table(settings['DYNAMODB_USER_TABLE'])
        self.expense_index = self.dynamodb.Table(settings['DYNAMODB_EXPENSE_TABLE'])

    def get_user(self, id):
        """
        Returns user connected with the id(if exists)
        :param id: str (as email)
        :return: User
        """
        response = self.user_index.get_item(
            Key={'CustomerId': id}
        )
        print(response['Item'])
        try:
            user_obj: User = User(
                id=response['Item']['CustomerId'],
                name=response["Item"]["Name"],
                expense_ids=response["Item"]["Expenses"],
                friend_ids=response["Item"]["Friends"]
            )
        except IndexError:
            raise UserNotFound
        return user_obj

    def get_all_users(self):
        """
        Get all users from the repository
        :return:
        """
        return self.user_index.get_items()['Items']

    def add_user(self, user: User):
        """
        Add user to the repository if user does not exist
        :param user:
        :return:
        """
        # TODO
        if self.user_index.get(user.id) is not None:
            raise UserExists

        self.user_index[user.id] = user
        return user.id

    def add_friend(self, user_id: str, friend_id: str):
        """
        Add friend (both directions)
        :param user_id: str
        :param friend_id:  str
        :return:None
        """
        friend: User = self.get_user(friend_id)
        user: User = self.get_user(user_id)

        def add_friend_helper(table, id, fid):
            response = table.update_item(
                Key={
                    'CustomerId': id
                },
                UpdateExpression="set Friends = list_append(if_not_exists(Friends,:empty_list), :i)",
                ExpressionAttributeValues={
                    ':i': [fid],
                    ':empty_list': []
                },
                ReturnValues="UPDATED_NEW"
            )
            return response

        # Adding friends (both ways)
        add_friend_helper(self.user_index, user_id, friend_id)
        add_friend_helper(self.user_index, friend_id, user_id)

    def update_user(self, id, field, data=None):
        """Update data for the specified video."""
        # TODO
        user_obj = self.get_user(id)
        # Set field attribute to data arg
        setattr(user_obj, field, data)

    ####################################################################################################################
    def get_expense(self, id):
        """
        Returns the expense connected with the id(if exists)
        :param id: int
        :return: Expense
        """
        try:
            response = self.expense_index.get_item(
                Key={'ExpenseId': id}
            )
            expense_obj: Expense = Expense(
                id=id,
                user_id=response['Item']["For"],
                payor=response['Item']["By"],
                amount=response['Item']["Amount"],
                description=response["Item"]["Description"],
                comments=response["Item"]["Comments"],
                date=response["Item"]["Date"]
            )
        except IndexError:
            raise ExpenseNotFound

        return expense_obj

    def update_expense(self, id, field, data=None):
        # TODO
        """Update data for the specified expense."""
        exp_obj: Expense = self.get_expense(id)
        # Set field attribute to data arg
        setattr(exp_obj, field, data)
        return exp_obj

    def delete_expense(self, id):
        """Delete the specified expense."""
        exp_obj: Expense = self.get_expense(id)
        payor = self.get_user(exp_obj.payor)
        payee = self.get_user(exp_obj.user_id)
        payee_expenses = payee.expense_ids
        payee_expenses.remove(id)
        # TODO if None put an empty list
        self.expense_index.delete_item(
            Key={
                'ExpenseId': id
            }
        )

        self.user_index.update_item(
            Key={
                'CustomerId': exp_obj.user_id
            },
            UpdateExpression="set Expenses = :i",
            ExpressionAttributeValues={
                ':i': payee_expenses,
            },
            ReturnValues="UPDATED_NEW"
        )

        if exp_obj.payor != exp_obj.user_id:
            payor_expenses = payor.expense_ids
            payor_expenses.remove(id)
            self.user_index.update_item(
                Key={
                    'CustomerId': exp_obj.payor
                },
                UpdateExpression="set Expenses = :i",
                ExpressionAttributeValues={
                    ':i': payor_expenses,
                },
                ReturnValues="UPDATED_NEW"
            )

    def add_expense(self, exp: Expense):
        """Adds an expense object to the repository."""
        payee: User = self.get_user(exp.user_id)
        payor: User = self.get_user(exp.payor)

        response = self.expense_index.put_item(
            Item={
                'ExpenseId': exp.id,
                'Amount': exp.amount,
                'Date': exp.date,
                'Description': exp.description,
                'Comments': exp.comments,
                'For': exp.user_id,
                'By': exp.payor
            }
        )
        print(f"Expense response {response}")
        self.__expense_helper__(exp.id, exp.payor)
        if exp.user_id != exp.payor:
            self.__expense_helper__(exp.id, exp.user_id)

    def __expense_helper__(self, exp_id, user_id):
        """
        Adds expenses to user document too
        :param exp_id: expense id
        :param user_id: id of user affected by the expense
        :return:
        """
        response = self.user_index.update_item(
            Key={
                'CustomerId': user_id
            },
            UpdateExpression="set Expenses = list_append(if_not_exists(Expenses,:empty_list), :i)",
            ExpressionAttributeValues={
                ':i': [exp_id],
                ':empty_list': []
            },
            ReturnValues="UPDATED_NEW"
        )
        return response
