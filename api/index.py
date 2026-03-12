import os
from flask import Flask, render_template, request, redirect, url_for, flash
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/..')
from app import app as flask_app

app = Flask(__name__)
app.secret_key = flask_app.secret_key

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
    return flask_app.wsgi_app(request.environ)

if __name__ == '__main__':
    flask_app.run()

