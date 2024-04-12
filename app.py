from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv
import logging

from routes.sod import sod
from routes.retail import retail

load_dotenv()

app = Flask(__name__)
CORS(app)
app.register_blueprint(sod, url_prefix="/sod")
app.register_blueprint(retail, url_prefix="/retail")
app.logger.setLevel(logging.INFO)


if __name__ == "__main__":
    app.run()

""" venv\Scripts\activate to activate the virtual environment"""  # type: ignore


@app.route("/")
def hello_world():
    return "Hello, World (of Warcraft)!"
