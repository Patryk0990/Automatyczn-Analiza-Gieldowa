from Database.databasewrapper import DatabaseWrapper
from User.client import Client
from User.privileged_client import PrivilegedClient
from User.admin import Admin
import hashlib
import re


class UserManager:

    @staticmethod
    def validate_email(string):
        if re.fullmatch(r'[A-Za-z0-9.]+@[A-Za-z0-9]+\.[A-Z|a-z]{2,}', string):
            return True
        return False

    @staticmethod
    def validate_username(string):
        if re.fullmatch(r'[A-Za-z0-9@#$%^&+=!_-]{6,32}', string):
            return True
        return False

    @staticmethod
    def validate_password(string):
        if re.fullmatch(r'^(?=.*[A-Z])(?=.*[a-z])(?=.*[0-9])(?=.*[@#$%^&+=!._-])[A-Za-z0-9@#$%^&+=!._-]{8,100}$', string):
            return True
        return False

    @staticmethod
    def authenticate_user(username, password):
        password = hashlib.sha3_512(password.encode()).hexdigest()
        db = DatabaseWrapper()
        result = db.read("users", username=username, password=password)
        if result is not None and result:
            result = result[0]
            return {
                'id': result[0],
                'username': result[2],
                'permission_level': result[4],
                'authenticated': True,
                'active': result[5]
            }
        return None

    @staticmethod
    def load_user(user_id, username, permission_level, authenticated, active):
        if permission_level == 0:
            return Client(user_id, username, permission_level, authenticated, active)
        elif permission_level == 1:
            return PrivilegedClient(user_id, username, permission_level, authenticated, active)
        elif permission_level == 2:
            return Admin(user_id, username, permission_level, authenticated, active)
        return None

    @staticmethod
    def get_users():
        users = []
        db = DatabaseWrapper()
        for u in db.read("users"):
            users.append({
                'id': u[0],
                'username': u[2],
                'permission_level': u[4],
                'active': u[5]
            })
        return users

    @staticmethod
    def get_user_by_id(user_id):
        db = DatabaseWrapper()
        result = db.read("users", id=user_id)
        if result is not None and result:
            result = result[0]
            return result
        return None

    @staticmethod
    def get_user_by_username(username):
        db = DatabaseWrapper()
        result = db.read("users", username=username)
        if result is not None and result:
            result = result[0]
            return result
        return None

    @staticmethod
    def get_user_by_email(email):
        db = DatabaseWrapper()
        result = db.read("users", email=email)
        if result is not None and result:
            result = result[0]
            return result
        return None

    @staticmethod
    def create_user(username, email, password):
        password = hashlib.sha3_512(password.encode()).hexdigest()
        db = DatabaseWrapper()
        user_id = db.create("users", **{
            "username": username,
            "email": email,
            "password": password,
        })
        if user_id is not None:
            if db.create("users_interface_settings", **{"user_id": user_id}) and db.create("users_api_settings", **{"user_id": user_id}):
                return True
            else:
                UserManager.delete_user(user_id)
        return None

    @staticmethod
    def update_user(user_id, **kwargs):
        if kwargs.get("password"):
            kwargs["password"] = hashlib.sha3_512(kwargs.get("password").encode()).hexdigest()
        db = DatabaseWrapper()
        return db.update("users", user_id, **kwargs)

    @staticmethod
    def delete_user(user_id):
        db = DatabaseWrapper()
        return db.delete("users", user_id)

    @staticmethod
    def get_user_interface_settings(user_id):
        db = DatabaseWrapper()
        result = db.read("users_interface_settings", user_id=user_id)
        if result is not None and result:
            result = result[0]
            return {
                "dark_mode": result[2],
                "theme_mode": result[3],
                "font_size": result[4]
            }
        return None

    @staticmethod
    def get_user_api_settings(user_id):
        db = DatabaseWrapper()
        result = db.read("users_api_settings", user_id=user_id)
        if result is not None and result:
            result = result[0]
            return {
                "apca_api_key_id": result[2],
                "apca_api_secret_key": result[3]
            }
        return None

    @staticmethod
    def update_user_interface_settings(user_id, **kwargs):
        db = DatabaseWrapper()
        return db.update("users_interface_settings", user_id, **kwargs)

    @staticmethod
    def update_user_api_settings(user_id, **kwargs):
        db = DatabaseWrapper()
        return db.update("users_api_settings", user_id, **kwargs)

