from Server.server import Server
from Server.config import DevelopmentConfig


if __name__ == '__main__':

    server = Server(DevelopmentConfig)
    server.run(use_reloader=False)
