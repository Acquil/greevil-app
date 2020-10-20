"""
Repository of users and expenses that uses in-memory objects, no serialization.
Used for testing only.
"""

from . import User, Expense, ExpenseNotFound, UserNotFound, UserExists


class Repository(object):
    """In-Memory repository."""

    def __init__(self, settings):
        """Initializes the repository. Note that settings are not used."""
        self.name = 'In-Memory'
        self.user_index = {}
        self.expense_index = {}

    def get_user(self, id):
        """
        Returns user connected with the id(if exists)
        :param id: str (as email)
        :return: User
        """
        user_obj: User = self.user_index.get(id)
        if user_obj is None:
            raise UserNotFound
        return user_obj

    def get_all_users(self):
        """
        Get all users from the repository
        :return:
        """
        return self.user_index.values()

    def add_user(self, user: User):
        """
        Add user to the repository if user does not exist
        :param user:
        :return:
        """
        if self.user_index.get(user.id) is not None:
            raise UserExists

        self.user_index[user.id] = user
        return user.id

    def add_friend(self, user_id: str, friend_id: str):
        """
        Add friend (both directions)
        :param user_id: str
        :param friend_id:  str
        :return:
        """
        friend: User = self.get_user(friend_id)
        user: User = self.get_user(user_id)
        user.friend_ids.append(friend_id)
        friend.friend_ids.append(user_id)

        user.friend_ids = list(set(user.friend_ids))
        friend.friend_ids = list(set(friend.friend_ids))

    def update_user(self, id, field, data=None):
        """Update data for the specified video."""
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
        expense_obj: Expense = self.expense_index.get(id)
        if expense_obj is None:
            raise ExpenseNotFound

        return expense_obj

    def update_expense(self, id, field, data=None):
        """Update data for the specified expense."""
        exp_obj: Expense = self.get_expense(id)
        # Set field attribute to data arg
        setattr(exp_obj, field, data)
        return exp_obj

    def add_expense(self, exp: Expense):
        """Adds an expense object to the repository."""
        self.expense_index[exp.id] = exp
        payee: User = self.get_user(exp.user_id)
        payor: User = self.get_user(exp.payor)

        payee.expense_ids.append(exp.id)
        if exp.user_id != exp.payor:
            payor.expense_ids.append(exp.id)
