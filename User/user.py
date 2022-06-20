from abc import ABC, abstractmethod


class User(ABC):

    def __init__(self, user_id, username, permission_level, authenticated=False, active=False):
        self.__id = user_id
        self.__username = username
        self.__permission_level = permission_level
        self.__authenticated = authenticated
        self.__active = active

    def is_authenticated(self):
        return self.__authenticated

    def is_active(self):
        return self.__active

    def get_id(self):
        return self.__id

    def get_username(self):
        return self.__username

    def __dict__(self):
        result = {
            'id': self.__id,
            'username': self.__username,
            'permission_level': self.__permission_level,
            'authenticated': self.__authenticated,
            'active': self.__active
        }
        return result

    @staticmethod
    @abstractmethod
    def is_privileged():
        return False

    @staticmethod
    @abstractmethod
    def is_superuser(self):
        return False
