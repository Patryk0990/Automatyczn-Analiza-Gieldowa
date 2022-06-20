# Flask environment config

class Config:
    SECRET_KEY = 'c1de48fcde117953577c0e7b7c01db02'


class ProductionConfig(Config):
    DEBUG = False
    TESTING = False
    ENV = 'production'


class DevelopmentConfig(Config):
    DEBUG = True
    TESTING = True
    ENV = "development"


STATIC_URL_PATH = ''
STATIC_FOLDER = 'Routes/Static'
TEMPLATE_FOLDER = 'Routes/Templates'
