#!/usr/bin/env python
from flask import Flask
from flask_cors import CORS

from apis import api

app = Flask(__name__)

# CORS
cors = CORS(app, resources={r"/*": {"origins": "*"}})

api.init_app(app)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8000)
