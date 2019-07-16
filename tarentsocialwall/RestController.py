#!flask/bin/python
import os
# import ssl
import uuid
from datetime import timedelta
from urllib.parse import urlsplit, parse_qs

from apscheduler.schedulers.background import BackgroundScheduler
from dateutil import parser
from flask import jsonify, make_response, Flask, request, abort, json
from flask_cors import CORS
from flask_jwt_extended import create_access_token, JWTManager, jwt_required, get_jwt_identity, \
    jwt_refresh_token_required
from http import HTTPStatus
from passlib.hash import sha256_crypt

from tarentsocialwall import SocialWallPostFetcher
from tarentsocialwall.Authenticate import Authenticate
from tarentsocialwall.AuthenticateLDAP import AuthenticateLDAP
from tarentsocialwall.SocialPost import SocialPost
from tarentsocialwall.SocialWallPostFetcher import fetch_posts_job
from tarentsocialwall.User import User
from tarentsocialwall.Util import Util


app = Flask(__name__)
CORS(app)

app.config['JWT_SECRET_KEY'] = Util.randomString()  # After every start a new password. Sorry user, security first

jwt = JWTManager(app)

mongoClient = SocialWallPostFetcher.mongoClient

auth = Authenticate()
auth_ldap = AuthenticateLDAP()

ROOT_PATH = os.environ.get('ROOT_PATH')

scheduler = None

# ctx = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
# ctx.load_cert_chain('sert/cert.pem', 'sert/key.pem')

def identity(payload):
    user_id = payload['identity']
    return auth.userid_table.get(user_id, None)

def response_ok(data):

    responseMsg = {'status': HTTPStatus.OK, 'msg': data}
    response = app.response_class(
        response=json.dumps(responseMsg),
        status=HTTPStatus.OK,
        mimetype='application/json'
    )
    return response

def response_server_error(data):

    responseMsg = {'status': HTTPStatus.INTERNAL_SERVER_ERROR, 'msg': data}

    response = app.response_class(
        response=json.dumps(responseMsg),
        status=HTTPStatus.HTTPStatus.INTERNAL_SERVER_ERROR,
        mimetype='application/json'
    )
    return response

def response_not_found(data):
    responseMsg = {'status': HTTPStatus.NOT_FOUND, 'msg': data}
    response = app.response_class(
        response=json.dumps(responseMsg),
        status=HTTPStatus.NOT_FOUND,
        mimetype='application/json'
    )
    return response

def response_bad_request(data):
    responseMsg = {'status': HTTPStatus.BAD_REQUEST, 'msg': data}
    response = app.response_class(
        response=json.dumps(responseMsg),
        status=HTTPStatus.BAD_REQUEST,
        mimetype='application/json'
    )
    return response

@app.route('/login', methods=['POST'])
def login():
    if not request.is_json:
        return jsonify({"msg": "Missing JSON in request"}), HTTPStatus.BAD_REQUEST

    username = request.json.get('username', None)
    password = request.json.get('password', None)
    if not username:
        return jsonify({"msg": "Missing username parameter"}), HTTPStatus.BAD_REQUEST
    if not password:
        return jsonify({"msg": "Missing password parameter"}), HTTPStatus.BAD_REQUEST

    user = None

    if eval(os.environ.get('LDAP-USE')):
        try:
            user= auth_ldap.authenticate_user(username, password)
            if user is None:
                print("User %s not found" % username)
                return jsonify({"msg": "User %s not found in ldap" % username}), HTTPStatus.BAD_REQUEST
            else:
                print("User %s found" % username)
        except Exception as ex:
            print(ex)
            return jsonify({"msg": "Exception by ldap"}), HTTPStatus.INTERNAL_SERVER_ERROR
    if eval(os.environ.get('DEFAULT-AUTH')):
        if user is None:
            if auth.authenticate_user(username, password) is None:
                return jsonify({"msg": "Bad username or password"}), HTTPStatus.UNAUTHORIZED

    # Identity can be any data that is json serializable
    access_token = create_access_token(identity=username)
    return jsonify(access_token=access_token), HTTPStatus.OK


# The jwt_refresh_token_required decorator insures a valid refresh
# token is present in the request before calling this endpoint. We
# can use the get_jwt_identity() function to get the identity of
# the refresh token, and use the create_access_token() function again
# to make a new access token for this identity.
@app.route('/refresh', methods=['POST'])
@jwt_refresh_token_required
def refresh():
    current_user = get_jwt_identity()
    return jsonify(access_token=create_access_token(identity=current_user)), HTTPStatus.OK


# social posts
@app.route('/socialposts')
def index():
    try:
        social_post = mongoClient.get_random_social_post()
        if social_post is None:
            response_not_found('No entries for social_post in the database')
        else:
            resp = make_response(jsonify(social_post.__dict__))
            resp.headers['Access-Control-Allow-Origin'] = '*'
            return resp
    except Exception as e:
        print(e)
        abort(HTTPStatus.INTERNAL_SERVER_ERROR)


@app.route('/socialposts/google')
def google_posts():
    try:
        google_post_list = mongoClient.get_google_calendar_posts()

        if google_post_list is None or len(google_post_list) == 0:
            response_not_found('No entries for google_post in the database')
        else:
            resp = make_response(jsonify([item.__dict__ for item in google_post_list]))
            resp.headers['Access-Control-Allow-Origin'] = '*'
            return resp

    except Exception as e:
        print(e)
        abort(HTTPStatus.INTERNAL_SERVER_ERROR)


# custom posts
@app.route('/customposts')
@jwt_required
def custom_posts():
    current_user = get_jwt_identity()
    print("User(id='%s')" % current_user)

    custom_post_list = mongoClient.get_custom_social_post()

    if custom_post_list is None:
        response_not_found('No entries for custom_post in the database')
    else:
        resp = make_response(jsonify([item.__dict__ for item in custom_post_list]))
        resp.headers['Access-Control-Allow-Origin'] = '*'
        return resp


@app.route('/customposts/create', methods=['POST'])
@jwt_required
def create_post():
    current_user = get_jwt_identity()
    social_post = None

    if request.json:
        social_post = create_post_from_request(request.json)
        social_post.author = get_jwt_identity()
        social_post.externalId = str(uuid.uuid1())
        mongoClient.write_social_post(social_post)
    else:
        response_bad_request(request.json)

    return response_ok(social_post.title)


@app.route('/customposts/update', methods=['POST'])
@jwt_required
def update_post():

    social_post = None

    if request.json:
        content = request.json
        social_post = create_post_from_request(request.json)
        social_post.author = get_jwt_identity()
        social_post.externalId = content['externalId']
        mongoClient.write_social_post(social_post)
    else:
        response_bad_request(request.json)

    return response_ok(social_post.title)


def create_post_from_request(content):
    social_post = SocialPost()
    social_post.title = content['title']
    social_post.text = content['text']
    social_post.created = Util.convert_date_to_UTC_time_stamp(parser.isoparse(content["created"]))
    social_post.source = "custom post"
    social_post.validTo = Util.convert_date_to_UTC_time_stamp(parser.isoparse(content["end"]))
    social_post.validFrom = Util.convert_date_to_UTC_time_stamp(
        parser.isoparse(content["start"]) - timedelta(weeks=3))
    if 'image' in content is not None and len(content['image']) > 0:
        social_post.image = content['image']
    social_post.start = Util.convert_date_to_UTC_time_stamp(parser.isoparse(content["start"]))
    social_post.end = Util.convert_date_to_UTC_time_stamp(parser.isoparse(content["end"]))
    return social_post


@app.route('/customposts/delete/<string:external_id>', methods=['DELETE'])
@jwt_required
def delete_post(external_id):
    if len(external_id) > 0:
        mongoClient.delete_post(external_id)
    else:
        response_bad_request(external_id)

    return response_ok('custom post %s deleted' % external_id)


@app.route('/callback')
def insta_callback():
    query = urlsplit(request.url).query
    params = parse_qs(query)

    print(params['code'][0])

    SocialWallPostFetcher.instagramConnector.init_instagram_connector(params['code'][0])

    for instaPost in SocialWallPostFetcher.instagramConnector.fetch_posts():
        mongoClient.writeSocialPost(instaPost)

    return HTTPStatus.OK


# users
@app.route('/users')
@jwt_required
def users():
    try:
        user_list = mongoClient.get_users()
        if user_list is None:
            response_not_found('No entries for users in the database')
        else:
            resp = make_response(jsonify([item.__dict__ for item in user_list]))
            resp.headers['Access-Control-Allow-Origin'] = '*'
            return resp
    except Exception as e:
        print(e)
        abort(HTTPStatus.INTERNAL_SERVER_ERROR)


@app.route('/users/create', methods=['POST'])
@jwt_required
def create_user():

    user = None

    if eval(os.environ.get('LDAP-USE')):
        response_bad_request('LDAP is used, the function is not available')

    if request.json:
        user = create_user_from_request(request.json)
        mongoClient.write_user(user)
    else:
        response_bad_request(request.json)

    return response_ok('user %s created' % user.username)



@app.route('/users/update', methods=['POST'])
@jwt_required
def update_user():

    user = None

    if eval(os.environ.get('LDAP-USE')):
        response_bad_request('LDAP is used, the function is not available')
    if request.json:
        user = create_user_from_request(request.json)
        mongoClient.write_user(user)
    else:
        response_bad_request(request.json)

    return response_ok('user %s updated' % user.username)


@app.route('/users/delete/<string:username>', methods=['DELETE'])
@jwt_required
def delete_user(username):
    if eval(os.environ.get('LDAP-USE')):
        response_bad_request('LDAP is used, the function is not available')
    if len(username) > 0:
        mongoClient.delete_post(username)
    else:
        response_bad_request(username)

    return response_ok('user %s deleted' % username)

@app.route('/status')
def get_status():
    if scheduler is None:
        return 'scheduler is none'
    else:
        return 'scheduler is running: %s' % scheduler.running


def create_user_from_request(content):
    user = User()
    user.username = content['username']
    user.password = sha256_crypt.hash(content['password'])
    user.firstname = content['firstname']
    user.lastname = content['lastname']
    return user


def job_function():
    fetch_posts_job()


if __name__ == '__main__':
    scheduler = BackgroundScheduler()
    minutes = int(os.environ.get('INTERVAL'))
    print(minutes)
    scheduler.add_job(job_function, 'interval', minutes=minutes)
    scheduler.start()
    app.run(debug=eval(os.environ.get('DEBUG')), host='0.0.0.0', port=os.environ.get('PORT'))


