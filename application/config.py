import os 
basedir = os.path.abspath(os.path.dirname(__file__))

# setting up base configuration class
class Config():
    DEBUG = False 
    SQLITE_DB_DIR = None
    SQLALCHEMY_DATABASE_URI = None 
    SECRET_KEY = None 
    UPLOADED_PHOTOS_DEST = None

# setting up local development configurations
class LocalDevelopmentConfig(Config):
    SQLITE_DB_DIR = os.path.join(basedir,"../db_directory")
    SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(SQLITE_DB_DIR,"BlogLite.sqlite3")
    SECRET_KEY = 'mysecretkey'
    UPLOADED_PHOTOS_DEST = os.path.join(basedir,"../static/images")
    DEBUG = True 
