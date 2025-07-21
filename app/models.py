from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
import uuid  # to generate API keys

db = SQLAlchemy()       # the database instance
bcrypt = Bcrypt()       # for hashing passwords

def generate_api_key():
    return str(uuid.uuid4())  # makes a unique key like 'ad2342ef-...'

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    api_key = db.Column(db.String(36), unique=True, default=generate_api_key)

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)

from datetime import datetime

class WeatherRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    city = db.Column(db.String(100), nullable=False)
    temperature = db.Column(db.Float, nullable=False)
    description = db.Column(db.String(255), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

