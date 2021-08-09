import base64
import json
import os
import datetime
from functools import wraps

import jwt
from flask import Flask, jsonify, make_response
from flask import request
from flask_pymongo import PyMongo
from flask_swagger_ui import get_swaggerui_blueprint
from flask_mongoengine import MongoEngine

app = Flask(__name__)

# MongoDB Configuration
app.config['MONGODB_SETTINGS'] = {
    'db': 'assignmentsDB',
    'host': 'localhost',
    'port': 27017,
    'username': base64.b16decode(os.getenv('MONGO_UNAME')),
    'password': base64.b16decode(os.getenv('MONGO_PASS')),
    'authentication_source': base64.b16decode(os.getenv('MONGO_USER'))
}

mongo = MongoEngine(app)  # MongoDB Object

# JWT Secret Config
app.config['SECRET_KEY'] = base64.b16decode(os.getenv('SECRET_KEY'))


# Validate JWT Token
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):

        try:
            token = request.args.get('token')  # http://localhost:5554/route?token=alshfjfjdklsfj89549834ur

            if not token:
                return jsonify({'message': 'Token is missing!'}), 403

            data = jwt.decode(token, app.config['SECRET_KEY'])
        except Exception as err:
            print('Error: ', err)
            return jsonify({'message': 'Token is invalid!'}), 403

        return f(*args, **kwargs)

    return decorated


# Swagger Configuration
SWAGGER_URL = '/swagger'
API_URI = '/static/swagger.yaml'
swagger_ui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URI,
    config={
        'app_name': 'Flask API Sample'
    }
)
app.register_blueprint(swagger_ui_blueprint, url_prefix=SWAGGER_URL)


@app.route('/login')
def login():
    auth = request.authorization

    if auth and auth.password == os.getenv('JWT_PASS'):
        token = jwt.encode({'user': auth.username, 'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=15)},
                           app.config['SECRET_KEY'])
        return jsonify({'token': token})

    return make_response('Could not verify!', 401, {'WWW-Authenticate': 'Basic realm="Login Required"'})


@app.route('/')
@token_required
def index():
    return 'Hello, This is a Sample API'


@app.route('/assignments', methods=['post'])
@token_required
def assignment_create():
    try:
        assignment_id = request.headers.get('id')
        name = request.headers.get('name')
        title = request.headers.get('title')
        description = request.headers.get('description')
        assignment_type = request.headers.get('type')
        duration = request.headers.get('duration')

        mongo.db.assignments.insert_one({'id': assignment_id, 'name': name, 'title': title, 'description': description,
                                         'type': assignment_type, 'duration': duration})

        status = {'message': 'Assignment Created..!'}, 201
    except Exception as err:
        status = {'message': 'Assignment Creation Failed..!'}, 500
        print('Error: Assignment Create: ', err)

    return jsonify(status)


@app.route('/findById', methods=['get'])
@token_required
def get_assignment_by_id():
    try:
        assignment_id = int(request.args.get('id'))
        status = list(mongo.db.assignments.find({'id': assignment_id}, {'_id': 0}))
        status = json.dumps(status, indent=4)
    except Exception as err:
        status = 'False', 500
        print('Error: Assignment findById: ', err)
    return status


@app.route('/findByTags', methods=['get'])
@token_required
def get_assignment_by_tag():
    try:
        assignment_id = int(request.args.get('id'))
        status = list(mongo.db.assignments.find({'id': assignment_id}, {'_id': 0}))
        status = json.dumps(status, indent=4)
    except Exception as err:
        status = 'False', 500
        print('Error: Assignment findById: ', err)
    return status


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5554)
