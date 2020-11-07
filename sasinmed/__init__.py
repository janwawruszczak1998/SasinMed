from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_admin import Admin
from sasinmed.config import name, db_name, password
from flask_migrate import Migrate
from datetime import timedelta


app = Flask(__name__)

# db and admin config
app.secret_key = 'w4lepsze'
app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://{name}:{password}@localhost:5432/{db_name}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['FLASK_ADMIN_SWATCH'] = 'cerulean'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=10)

db = SQLAlchemy(app)
migrate = Migrate(app, db)
admin = Admin(app)