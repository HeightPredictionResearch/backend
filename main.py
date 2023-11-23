from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

import os
import jwt
from datetime import timedelta, datetime
import cv2
from flask import make_response, request
from rembg import remove
from skimage.measure import regionprops

import base64
from io import BytesIO
from PIL import Image

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret'
CORS(app)

app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://postgres.xpteutzlujjsxknliwix:hariinikopi@aws-0-ap-southeast-1.pooler.supabase.com:6543/postgres"
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

@app.route('/')
def hello():
    return 'Welcome!'

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
    data = jwt.decode(token, key=app.config['SECRET_KEY'], algorithms='HS256')
    user_id = data['user_id']

    child = Child.query.filter_by(user_id=user_id, id=id).first()
    if not child:
        return make_response("Child not found", 404)
    
    return make_response({
        'id': child.id,
        'name': child.name,
        'birth_date': child.birth_date
    }, 200)

@app.route('/api/v1/predict', methods=['POST'])
def predictv1():
    # Get the file from post request
    image_base64 = request.json['image']

    # Extract the MIME type and base64 data
    mime_type, base64_string = image_base64.split(';base64,')
    image_format = mime_type.split('/')[-1]

    current_dateTime = datetime.now()
    filename = f'{current_dateTime.microsecond}.{image_format}'

    # Save the file to ./tmp
    save_path = os.path.join('/tmp', filename)

    # Decode the base64 string into bytes
    bytes_decoded = base64.b64decode(base64_string)

    # Open the image from bytes and save it to a file
    with Image.open(BytesIO(bytes_decoded)) as img:
        img.save(save_path)

    # Read the image
    image = cv2.imread(save_path)
    image = cv2.resize(image,(880, 1320))

    # Remove background
    image = remove(image)

    # Thersholding
    image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(image, 0, 255, cv2.THRESH_BINARY)
    
    props = regionprops(thresh)
    for p in props:
        majL = p.axis_major_length

    metrics_per_pixel = majL/92.5
    tinggi = majL/8.93

    os.remove(save_path)
    return make_response(f"{round(tinggi,1)}", 200)

@app.route('/api/v2/predict', methods=['POST'])
def predictv2():
    uploaded_file = request.files['image']
    child_id = request.form['child_id']
    taken_date = datetime.now()
    print(taken_date)

    # Check if the 'image' field was sent in the request
    if uploaded_file:
        current_dateTime = datetime.now()
        filename = f'{current_dateTime.microsecond}.{"png"}'

        # Save the file to ./tmp
        save_path = os.path.join('/tmp', filename)

        uploaded_file.save(save_path)

        # Read the image
        image = cv2.imread(save_path)
        image = cv2.resize(image,(880, 1320))

        # Remove background
        image = remove(image)

        # Thersholding
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        _, thresh = cv2.threshold(image, 0, 255, cv2.THRESH_BINARY)
        
        props = regionprops(thresh)
        for p in props:
            majL = p.axis_major_length

        metrics_per_pixel = majL/92.5
        tinggi = majL/8.93

        os.remove(save_path)

        data = ChildHeight(child_id=child_id, height=round(tinggi,1), taken_date=taken_date)
        db.session.add(data)
        db.session.commit()

        return make_response(f"{round(tinggi,1)}", 200)
    else:
        return make_response('Image not found in the request', 400)
    
@app.route('/api/v1/predict/<child_id>', methods=['GET'])
def getPredictionByChildId(child_id):
    child_height = ChildHeight.query.filter_by(child_id=child_id).all()
    result = []
    for height in child_height:
        result.append({
            'id': height.id,
            'child_id': height.child_id,
            'height': height.height,
            'taken_date': height.taken_date
        })
    return make_response(result, 200)

if __name__ == "__main__":
    # This is used when running locally only. When deploying to Google App
    # Engine, a webserver process such as Gunicorn will serve the app.
    app.run(host="0.0.0.0", port=8080, debug=True)