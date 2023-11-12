import jwt
from db import *
from main import app
from flask import make_response, request

from datetime import timedelta, datetime

@app.route('/api/v1/register', methods=['POST'])
def register():
    name = request.json['name']
    email = request.json['email']
    password = request.json['password']

    user = User(name=name, email=email, password=password)
    db.session.add(user)
    db.session.commit()
    return make_response("Success", 200)

@app.route('/api/v1/login', methods=['POST'])
def login():
    email = request.json['email']
    password = request.json['password']

    user = User.query.filter_by(email=email).first()
    if not user:
        return make_response("User not found", 404)

    if user.password != password:
        return make_response("Wrong password", 401)
    
    token = jwt.encode({
                'user_id': user.id,
                'exp' : datetime.utcnow() + timedelta(days = 1)
            }, key=app.config['SECRET_KEY'])

    return make_response(token, 200)