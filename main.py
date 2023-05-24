import os
from flask import Flask,url_for
from application.config import LocalDevelopmentConfig
from application.database import db
from flask_restful import Resource, Api
from application.forms import photos
from flask_uploads import configure_uploads

app = None 
api = None
def create_app():
    app = Flask(__name__)
    app.config.from_object(LocalDevelopmentConfig)

    # database initialization
    db.init_app(app)

    # flask uploads configuration
    configure_uploads(app, photos)

    # api initialization
    api = Api(app)
    app.app_context().push()
    return app,api

app,api = create_app()

from application.controllers import *

#import apis
from application.api import UserAPI,BlogAPI,ImageAPI
api.add_resource(UserAPI,"/api/user/<int:user_id>", "/api/user")
api.add_resource(BlogAPI,"/api/blog/<int:blog_id>","/api/blog")
api.add_resource(ImageAPI,"/api/image/<string:ImageURL>")


if __name__=='__main__':
    app.run(host = '0.0.0.0',port = 8000)