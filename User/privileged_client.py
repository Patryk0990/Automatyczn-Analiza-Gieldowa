from User.user import User


class PrivilegedClient(User):

    @staticmethod
    def is_privileged():
        return True

    @staticmethod
    def is_superuser():
        return False
