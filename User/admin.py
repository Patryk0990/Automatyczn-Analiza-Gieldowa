from User.user import User


class Admin(User):

    @staticmethod
    def is_privileged():
        return True

    @staticmethod
    def is_superuser():
        return True
