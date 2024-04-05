from dotenv import load_dotenv, dotenv_values
import os


load_dotenv()


class basesit():
    SQLALCHEMY_DATABASE_URI = os.getenv('SQLALCHEMY_DATABASE_URI')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = 'SECRET_KEY'