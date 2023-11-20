from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

from main import app

app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://postgres.xpteutzlujjsxknliwix:hariinikopi@aws-0-ap-southeast-1.pooler.supabase.com:6543/postgres"
# app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///db.sqlite3"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200))
    email = db.Column(db.String(120))
    password = db.Column(db.String(60))

    created_at = db.Column(db.DateTime, default=db.func.now())
    updated_at = db.Column(db.DateTime, default=db.func.now())

class Child(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    name = db.Column(db.String(200))
    birth_date = db.Column(db.Date)

    created_at = db.Column(db.DateTime, default=db.func.now())
    updated_at = db.Column(db.DateTime, default=db.func.now())

class ChildHeight(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    child_id = db.Column(db.Integer)
    height = db.Column(db.Float)
    taken_date = db.Column(db.DateTime, default=db.func.now())

    created_at = db.Column(db.DateTime, default=db.func.now())
    updated_at = db.Column(db.DateTime, default=db.func.now())
