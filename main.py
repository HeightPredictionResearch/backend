from flask import Flask
from flask_cors import CORS
app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret'
CORS(app)

@app.route('/')
def hello():
    return 'Welcome!'

try:
    from controller.auth_controller import *
    from controller.height_controller import *
    from db import *
except Exception as e:
    print(e)

if __name__ == "__main__":
    # This is used when running locally only. When deploying to Google App
    # Engine, a webserver process such as Gunicorn will serve the app.
    app.run(host="127.0.0.1", port=8080, debug=True)