from flask import Flask, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from datetime import timedelta
import os


application = Flask(__name__)
application.config.from_object(__name__)

#application.secret_key = os.urandom(24)
application.secret_key = "8b5ad1a5811c417dfc5ca02f1eac1b17bae6a4f1859320bde495f74ab5d821db"
application.permanent_session_lifetime = timedelta(days=365)

application.config['UPLOAD_FOLDER'] = 'uploads'
application.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///database.db"
application.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

global COOKIE_TIME_OUT
COOKIE_TIME_OUT = 60*60*24*7 #7 days

'''
application.config['MAIL_SERVER'] = os.environ.get('MAIL_SERVER')
application.config['MAIL_PORT'] = os.environ.get('MAIL_PORT')
application.config['MAIL_USE_SSL'] = os.environ.get('MAIL_USE_SSL')
application.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
application.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_DEFAULT_SENDER')
application.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
'''

db = SQLAlchemy(application)

login_manager = LoginManager(application)
login_manager.login_view = 'login'
