from flask_socketio import SocketIO


class SocketIOWrapper:

    def __init__(self, flask_app):
        self.__socketio = SocketIO(flask_app, async_mode='threading')

    def add_event(self, endpoint=None, handler=None, namespace=None):
        self.__socketio.on_event(endpoint, handler, namespace)

    def get_socketio_object(self):
        return self.__socketio
