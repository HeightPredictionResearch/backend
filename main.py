import os
from datetime import datetime
import cv2
from flask import Flask, request
from rembg import remove
from skimage.measure import regionprops

app = Flask(__name__)


@app.route('/')
def hello():
    return 'Welcome!'

@app.route('/predict', methods=['POST'])
def predict():
    # Get the file from post request
    image_file = request.files['image']
    current_dateTime = datetime.now()

    # Save the file to ./images
    save_path = os.path.join(os.getcwd(), 'images', f'{current_dateTime.microsecond}.jpg')
    image_file.save(save_path)

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
        print ('%5d %12.3f' % (p.label, p.major_axis_length))
        majL = p.axis_major_length

    metrics_per_pixel = majL/16
    tinggi = majL/56.03

    os.remove(save_path)
    return f"{round(tinggi,1)}"