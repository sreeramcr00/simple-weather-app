import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:

    # Load DATABASE_URL from Azure App Service or DevOps pipeline
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    SECRET_KEY = os.environ.get('SECRET_KEY')
    OPENWEATHER_API_KEY = os.environ.get('OPENWEATHER_API_KEY')
