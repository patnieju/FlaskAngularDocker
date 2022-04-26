import os,sys

class Config(object):
    SECRET_KEY = 'key'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///mercadona.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DEFAULT_THEME = None

class ProductionConfig(Config):
    DEBUG = True

    # Security
    SESSION_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_DURATION = 3600

    # PostgreSQL database
    SQLALCHEMY_DATABASE_URI = 'postgresql://{}:{}@{}:{}/{}'.format(
        os.getenv('POSTGRE_DATABASE_USER', 'pgadmin'),
        os.getenv('POSTGRE_DATABASE_PASSWORD', 'mercadona'),
        os.getenv('POSTGRE_DATABASE_HOST', 'localhost'),
        os.getenv('POSTGRE_DATABASE_PORT_INTERNAL', 5454), #5432
        os.getenv('POSTGRE_DATABASE_NAME', 'mercadona')
    )

    # print("SQLALCHEMY_DATABASE_URI::>'"+str(SQLALCHEMY_DATABASE_URI)+"'", flush=True, file=sys.stdout)
    # exit()

class DebugConfig(Config):
    DEBUG = True

config_dict = {
    'Production': ProductionConfig,
    'Debug': DebugConfig
}

def GetConfig(ConfigType):
    ConfigType=ConfigType.capitalize()
    if ConfigType in config_dict.keys():
        return config_dict[ConfigType]
    else:
        return None