from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv
import logging

from routes.api import api

load_dotenv()

app = Flask(__name__)
CORS(app)
app.register_blueprint(api, url_prefix="/api")
app.logger.setLevel(logging.INFO)


if __name__ == "__main__":
    app.run(debug=True, port=5001)


@app.route("/")
def hello_world():
    return "Hello, World (of Warcraft)!"
