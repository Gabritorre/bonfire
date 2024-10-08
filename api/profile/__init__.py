from datetime import datetime, timezone
from flask import Blueprint, jsonify, request
from config import db, safeguard
from models import Profile, User, Advertiser, AuthToken
from api.utils import hash_sha1, hash_secret, set_auth_token, verify_secret, get_auth_token
from .user import user
from .adv import adv

profile = Blueprint("profile", __name__, url_prefix="/profile")
profile.register_blueprint(user)
profile.register_blueprint(adv)


@profile.route("/signup", methods=["PUT"])
@safeguard
def signup():
	req = request.get_json()
	handle = req["handle"]
	pwd = req["password"]
	is_adv = req["is_adv"]
	profile = db.session.query(Profile).where(Profile.handle == handle).first()

	if profile:
		return jsonify({"error": "Username already taken"})
	if len(pwd) < 8:
		return jsonify({"error": "Password too short"})
	new_profile = Profile(handle=handle, password=hash_secret(pwd))
	db.session.add(new_profile)
	db.session.flush()
	if is_adv:
		new_advertiser = Advertiser(id=new_profile.id)
		db.session.add(new_advertiser)
	else:
		new_user = User(id=new_profile.id)
		db.session.add(new_user)
	db.session.flush()
	res = jsonify({"error": None})
	set_auth_token(new_profile, res)
	return res



@profile.route("/login", methods=["POST"])
@safeguard
def login():
	req = request.get_json()
	handle = req["handle"]
	pwd = req["password"]
	profile = db.session.query(Profile).where(Profile.handle == handle).first()

	if profile and verify_secret(pwd, profile.password):
		res = jsonify({"error": None})
		set_auth_token(profile, res)
		db.session.query(AuthToken).where(AuthToken.profile_id == profile.id, AuthToken.expiration_date < datetime.now(timezone.utc)).delete()
		db.session.flush()
		return res
	return jsonify({"error": "Invalid credentials"})



@profile.route("/logout", methods=["GET"])
@safeguard
def logout():
	token = get_auth_token(request.cookies)
	if not token:
		return jsonify({"error": "Invalid token"})

	db.session.query(AuthToken).where(AuthToken.value == hash_sha1(str(request.cookies.get("auth_token")))).delete()
	db.session.flush()
	res = jsonify({"error": None})
	res.set_cookie("auth_token", "", expires=0)
	return res


# Get the profile id of the current user, and whether they are an advertiser or not
@profile.route("/", methods=["GET"])
@safeguard
def get_token():
	token = get_auth_token(request.cookies)
	if not token:
		return jsonify({"error": "Invalid token"})

	if db.session.query(Advertiser).where(Advertiser.id == token.profile_id).first():
		return jsonify({"error": None, "id": token.profile_id, "is_adv": True})
	return jsonify({"error": None, "id": token.profile_id, "is_adv": False})


# Delete the profile of the current user
@profile.route("/", methods=["DELETE"])
@safeguard
def delete_profile():
	token = get_auth_token(request.cookies)
	if not token:
		return jsonify({"error": "Invalid token"})

	profile = db.session.get(Profile, token.profile_id)
	if profile:
		db.session.query(Profile).where(Profile.id == token.profile_id).delete()
		db.session.flush()
	res = jsonify({"error": None})
	res.set_cookie("auth_token", "", expires=0)
	return res
