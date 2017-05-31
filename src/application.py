#!flask/bin/python
from flask import Flask
from flaskrun import flaskrun
import json
from classes.db import Firebase

application = Flask(__name__)
db = Firebase()


@application.route('/', methods=['GET'])
def get():
    return '{"Output":"Hello World"}'


@application.route('/', methods=['POST'])
def post():
    return '{"Output":"Hello World"}'

@application.route('/space', methods=['GET'])
def return_space():
    posts = db.get_initial_posts()
    return posts

if __name__ == '__main__':
    flaskrun(application)
