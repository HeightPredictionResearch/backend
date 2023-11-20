from flask import make_response, request
import jwt
from db import *
from main import app

@app.route('/api/v1/child', methods=['POST'])
def create_child():
    token = request.headers['Authorization']
    data = jwt.decode(token, key=app.config['SECRET_KEY'], algorithms='HS256')
    user_id = data['user_id']

    name = request.json['name']
    birth_date = request.json['birth_date']

    child = Child(user_id=user_id, name=name, birth_date=birth_date)
    db.session.add(child)
    db.session.commit()
    return make_response("Success", 200)

@app.route("/api/v1/child", methods=['GET'])
def get_child():
    token = request.headers['Authorization']
    data = jwt.decode(token, key=app.config['SECRET_KEY'], algorithms='HS256')
    user_id = data['user_id']

    children = Child.query.filter_by(user_id=user_id).all()
    result = []
    for child in children:
        result.append({
            'id': child.id,
            'name': child.name,
            'birth_date': child.birth_date
        })
    return make_response(result, 200)

@app.route("/api/v1/child/<id>", methods=['GET'])
def get_child_by_id(id):
    token = request.headers['Authorization']
    data = jwt.decode(token, key=app.config['SECRET_KEY'])
    user_id = data['user_id']

    child = Child.query.filter_by(user_id=user_id, id=id).first()
    if not child:
        return make_response("Child not found", 404)
    
    return make_response({
        'id': child.id,
        'name': child.name,
        'birth_date': child.birth_date
    }, 200)