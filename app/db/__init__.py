"""
Package for the db models.
"""
import uuid
from datetime import datetime


class User(object):
    """A transcript object for use in db/repository"""

    def __init__(
            self,
            id="",
            name="",
            expense_ids=None,
            friend_ids=None,

    ):
        """Initializes the User Collection"""
        if friend_ids is None:
            friend_ids = []
        if expense_ids is None:
            expense_ids = []
        self.id = id
        self.name = name
        self.expense_ids = expense_ids
        self.friend_ids = friend_ids

    def to_dict(self):
        """
        Converts object to python dictionary
        """
        obj = {
            'id': self.id,
            'name': self.name,
            'expense_id': self.expense_ids,
            'friend_ids': self.friend_ids,
        }
        return obj


class Expense(object):
    """A transcript object for use in db/repository"""

    def __init__(
            self,
            id=str(uuid.uuid4()),
            user_id="",
            amount=None,
            description="",
            comments="",
            payor="",
            date=datetime.now().isoformat(),

    ):
        """
        Initializes the Expense Collection
        :param user_id:     str
        :param amount:      double
        :param description: str
        :param comments:    str
        :param payor:       str
        :param date:        datetime
        """
        self.id = id
        self.user_id = user_id
        self.amount = amount
        self.description = description
        self.comments = comments
        self.payor = payor
        self.date = date

    def to_dict(self):
        """
        Converts object to python dictionary
        """
        obj = {
            'id': self.id,
            'user_id': self.user_id,
            'amount': self.amount,
            'description': self.description,
            'comments': self.comments,
            'payor': self.payor,
            'date': self.date,

        }
        return obj


class RepositoryException(Exception):
    """
    Exception raised when an object in the repository is not found
    """


class UserNotFound(RepositoryException):
    """
    Exception raised when a User object couldn't be retrieved from the repository, usually because it does not exist
    """


class UserExists(RepositoryException):
    """
    Exception raised when a User object already exists
    """


class ExpenseNotFound(RepositoryException):
    """
    Exception raised when an Expense object couldn't be retrieved from the repository, usually because it does not exist
    """
