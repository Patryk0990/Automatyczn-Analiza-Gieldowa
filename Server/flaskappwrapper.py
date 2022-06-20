from flask import (Flask)
from Server.config import STATIC_URL_PATH, STATIC_FOLDER, TEMPLATE_FOLDER


class FlaskAppWrapper:

    def __init__(self, config):
        self.__app = Flask(
            __name__,
            static_url_path=STATIC_URL_PATH,
            static_folder=STATIC_FOLDER,
            template_folder=TEMPLATE_FOLDER
        )
        self.__app.config.from_object(config)

    def add_endpoint(self, endpoint=None, endpoint_name=None, handler=None, methods=['GET'], *args, **kwargs):
        self.__app.add_url_rule(endpoint, endpoint_name, handler, methods=methods, *args, **kwargs)

    def get_app_object(self):
        return self.__app
