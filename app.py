from flask import Flask

from sasinmed import app, db
from sasinmed.models import *


@app.route('/')
def hello_world():
    return 'Hello, World!'

if __name__ == '__main__':
    app.run(debug=True)