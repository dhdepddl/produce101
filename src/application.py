#!flask/bin/python
from flask import Flask
from flaskrun import flaskrun
import json
from firebase import FirebaseAuthentication, FirebaseApplication

application = Flask(__name__)



@application.route('/', methods=['GET'])
def get():
    return '{"Output":"Hello World"}'


@application.route('/', methods=['POST'])
def post():
    return '{"Output":"Hello World"}'


@application.route('/space', methods=['GET'])
def return_space():
    firebase = FirebaseApplication('https://your_storage.firebaseio.com', authentication=None)
    authentication = FirebaseAuthentication('kUFM5wAt2CkXtfKrglMjLPgNsuWsO33j1uKHMRyn', 'dhdepddl@gmail.com',
                                            extra={'id': 123})
    firebase.authentication = authentication
    result = firebase.get('/cards', None, {'print': 'pretty'})
    return result

if __name__ == '__main__':
    flaskrun(application)

