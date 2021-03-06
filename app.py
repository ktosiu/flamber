from flask import Flask, send_from_directory, jsonify, request, g, render_template, make_response
from flask_restful import Resource, Api
from flask_sqlalchemy import SQLAlchemy
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from marshmallow import Schema, fields
from datetime import datetime
from passlib.apps import custom_app_context as pwd_context
# from flask.ext.httpauth import HTTPBasicAuth
from itsdangerous import (TimedJSONWebSignatureSerializer
                          as Serializer, BadSignature, SignatureExpired)
from flask_jwt import JWT, jwt_required, current_identity

app = Flask(__name__)
app.config.from_object('config')
api = Api(app)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
manager = Manager(app)
manager.add_command('db', MigrateCommand)

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def index(path):
    return render_template('index.html')
    
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    username = db.Column(db.String(64), unique=True)
    email = db.Column(db.String(64), unique=True)
    password_hash = db.Column(db.String(128))
    flames = db.relationship('Flame', backref='user', lazy='dynamic')
    
    def hash_password(self, password):
        self.password_hash = pwd_context.encrypt(password)
        
    def verify_password(self, password):
        return pwd_context.verify(password, self.password_hash)
        
    def generate_auth_token(self):
        s = Serializer(app.config['SECRET_KEY'])
        return s.dumps({'id': self.id, 'name': self.name, 'email': self.email})
        
# @auth.verify_password
# def verify_password(username_or_token, password):
#     user = User.query.filter_by(username = "asd").first()
#     g.user = user
#     return True

def authenticate(username, password):
    user = User.query.filter_by(username=username).first()
    if not user or not user.verify_password(password):
        return None
    # g.user = user
    return user

# def identity(payload):
#     user_id = payload['identity']
#     return User.query.filter_by(id=user_id).first()
    
#jwt = JWT(app, authenticate, identity)
        
class UserSchema(Schema):
    id = fields.Integer()
    name = fields.String()
    username = fields.String()
    email = fields.Email()
    flames = fields.Nested('FlameSchema', exclude=['user'], many=True)
        
class Flame(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(140))
    pub_date = db.Column(db.DateTime)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    
    def __init__(self, text, user_id, pub_date=None):
        self.text = text
        if pub_date is None:
            self.pub_date = datetime.utcnow()
        self.user_id = user_id

class FlameSchema(Schema):
    id = fields.Integer()
    text = fields.String()
    pub_date = fields.DateTime()
    user = fields.Nested('UserSchema', only=['id'])

class Users(Resource):
    # decorators = [jwt_required()]
    def get(self):
        return jsonify({'users': [UserSchema().dump(i).data for i in User.query.all()]})
        
    def post(self):
        username = request.json.get('username')
        password = request.json.get('password')
        email = request.json.get('email')
        if username is None or password is None or email is None:
            return 400
        if User.query.filter_by(username = username).first() is not None:
            return 400
        user = User(username = username, email = email)
        user.hash_password(password)
        db.session.add(user)
        db.session.commit()
        return 200
        
class UsersId(Resource):
    def get(self, user_id):
        return jsonify({'user': UserSchema().dump(User.query.get(user_id)).data})
        
class Flames(Resource):
    # decorators = [jwt_required()]
    def post(self):
        flame = request.json['flame']
        f = Flame(text=flame['text'], user_id=1)
        db.session.add(f)
        db.session.commit()
        return 200
        
    def get(self):
        return jsonify({'flame': [FlameSchema().dump(i).data for i in Flame.query.all()]})
        
class FlamesId(Resource):
    def get(self, flame_id):
        return jsonify({'flames': FlameSchema().dump(Flame.query.get(flame_id)).data})
        
    def delete(self, flame_id):
        f = Flame.query.get(flame_id)
        db.session.delete(f)
        db.session.commit()
        return 200

class Auth(Resource):
    def post(self):
        username = request.json.get('username')
        password = request.json.get('password')
        user = authenticate(username, password)
        if user is not None:
            token = user.generate_auth_token()
            return make_response(jsonify({'token': token.decode('ascii')}), 200)
        return 401
        
api.add_resource(Users, '/users')
api.add_resource(Flames, '/flames')
api.add_resource(UsersId, '/users/<int:user_id>')
api.add_resource(FlamesId, '/flames/<int:flame_id>')
api.add_resource(Auth, '/auth/login')

if __name__ == "__main__":
    app.run(debug=True)