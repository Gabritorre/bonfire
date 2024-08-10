from flask import Blueprint, jsonify, request
from config import db, safeguard
from models import Profile, User, Advertiser, AuthToken
from datetime import datetime, timezone
from api.utils import hash_sha1, hash_secret, set_auth_token, verify_secret
from .user import user
from .adv import adv

profile = Blueprint("profile", __name__, url_prefix="/profile")
profile.register_blueprint(user)
profile.register_blueprint(adv)

@profile.route("/signup", methods=["PUT"])
@safeguard
def signup():
	req = request.get_json()
	handle = req.get("handle")
	pwd = req.get("password")
	is_adv = req.get("is_adv")
	profile = db.session.query(Profile).where(Profile.handle == handle).first()

	if profile:
		return jsonify({"error": "Username already taken"})
	else:
		new_profile = Profile(handle=handle, password=hash_secret(pwd), name=handle)
		db.session.add(new_profile)
		db.session.flush()
		if is_adv:
			new_advertiser = Advertiser(id=new_profile.id)
			db.session.add(new_advertiser)
		else:
			new_user = User(id=new_profile.id)
			db.session.add(new_user)
		db.session.commit()
		res = jsonify({"error": None})
		set_auth_token(new_profile, res)
		return res



@profile.route("/login", methods=["POST"])
@safeguard
def login():
	req = request.get_json()
	handle = req.get("handle")
	pwd = req.get("password")
	profile = db.session.query(Profile).where(Profile.handle == handle).first()

	if profile and verify_secret(pwd, profile.password):
		res = jsonify({"error": None})
		set_auth_token(profile, res)
		return res
	return jsonify({"error": "Invalid credentials"})



@profile.route("/logout", methods=["GET"])
@safeguard
def logout():
	if ("auth_token" in request.cookies):
		db.session.query(AuthToken).where(AuthToken.value == hash_sha1(str(request.cookies.get("auth_token")))).delete()
		db.session.commit()
		res = jsonify({"error": None})
		res.set_cookie("auth_token", "", expires=0)
		return res
	return jsonify({"error": "Invalid token"})



@profile.route("/", methods=["GET"])
@safeguard
def get_token():
	if ("auth_token" in request.cookies):
		token = db.session.query(AuthToken).where(AuthToken.value == hash_sha1(str(request.cookies.get("auth_token"))), AuthToken.expiration_date > datetime.now(timezone.utc)).first()
		if token:
			if db.session.query(Advertiser).where(Advertiser.id == token.profile_id).first():
				return jsonify({"error": None, "id": token.profile_id, "is_adv": True})
			return jsonify({"id": token.profile_id, "is_adv": False, "error": None})
	return jsonify({"error": "Invalid token"})



@profile.route("/", methods=["DELETE"])
@safeguard
def delete_profile():
	if ("auth_token" in request.cookies):
		token = db.session.query(AuthToken).where(AuthToken.value == hash_sha1(str(request.cookies.get("auth_token"))), AuthToken.expiration_date > datetime.now(timezone.utc)).first()
		if token:
			profile = db.session.get(Profile, token.profile_id)
			if profile:
				db.session.query(Profile).where(Profile.id == token.profile_id).delete()
				db.session.commit()
			res = jsonify({"error": None})
			res.set_cookie("auth_token", "", expires=0)
			return res
	return jsonify({"error": "Invalid token"})
