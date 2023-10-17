import os
from datetime import datetime
import cv2
from flask import Flask, request
from rembg import remove
from skimage.measure import regionprops
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

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
        majL = p.axis_major_length

    metrics_per_pixel = majL/92.5
    tinggi = majL/8.93

    os.remove(save_path)
    print(round(tinggi,1))
    return f"{round(tinggi,1)}"

if __name__ == "__main__":
    # This is used when running locally only. When deploying to Google App
    # Engine, a webserver process such as Gunicorn will serve the app.
    app.run(host="127.0.0.1", port=8080, debug=True)