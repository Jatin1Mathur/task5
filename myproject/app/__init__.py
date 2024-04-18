from flask import Flask
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from flask_mail import Mail
from flask_jwt_extended import JWTManager


from app.models.model import db
from config import basesit

bcrypt = Bcrypt()
jwt = JWTManager()
migrate = Migrate()
mail = Mail()


def create_app():
    app = Flask(__name__)
    app.config.from_object(basesit)
    db.init_app(app)
    bcrypt.init_app(app)
    jwt.init_app(app)
    migrate.init_app(app, db)
    mail.init_app(app)
    from app.api import commant, follow, like, post, user
    app.register_blueprint(user.blueprint)
    app.register_blueprint(follow.blueprint)
    app.register_blueprint(like.blueprint)
    app.register_blueprint(post.blueprint)
    app.register_blueprint(commant.blueprint)
    return app