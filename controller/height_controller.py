from main import app
from db import *

import os
from datetime import datetime
import cv2
from flask import make_response, request
from rembg import remove
from skimage.measure import regionprops

import base64
from io import BytesIO
from PIL import Image

@app.route('/api/v1/predict', methods=['POST'])
def predictv1():
    # Get the file from post request
    image_base64 = request.json['image']

    # Extract the MIME type and base64 data
    mime_type, base64_string = image_base64.split(';base64,')
    image_format = mime_type.split('/')[-1]

    current_dateTime = datetime.now()
    filename = f'{current_dateTime.microsecond}.{image_format}'

    # Save the file to ./images
    save_path = os.path.join(os.getcwd(), 'images', filename)

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

        # Save the file to ./images
        save_path = os.path.join(os.getcwd(), 'images', filename)

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