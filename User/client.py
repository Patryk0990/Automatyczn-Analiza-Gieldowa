from User.user import User


class Client(User):

    @staticmethod
    def is_privileged():
        return False

    @staticmethod
    def is_superuser():
        return False
