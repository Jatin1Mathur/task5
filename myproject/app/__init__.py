from flask import Flask, request, jsonify
from flask_migrate import Migrate
from app.models.model import  db
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity

from urllib.parse import unquote_plus, quote_plus
from config import basesit
import os

bcrypt = Bcrypt()
jwt = JWTManager()
migrate = Migrate()



def create_app():

    app = Flask(__name__)
    app.config.from_object(basesit)
    db.init_app(app)
    bcrypt.init_app(app)
    jwt.init_app(app)
    migrate.init_app(app, db)
    


    from app.api import commant , follow , like , post , user
    app.register_blueprint(user.bluep)
    app.register_blueprint(follow.bluep)
    app.register_blueprint(like.bluep)
    app.register_blueprint(post.bluep)
    app.register_blueprint(commant.bluep)





    return app