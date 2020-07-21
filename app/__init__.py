from flask import Flask
from flask_login import LoginManager

from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate


app = Flask(__name__)
app.config.from_object(Config)

# DB stuff
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# login manager
login = LoginManager(app)
login.login_view = 'login'
login.login_message = "Пожалуйста, войдите, чтобы открыть эту страницу."

from app import routes, models

#print('Recreating all db')
#db.create_all()

