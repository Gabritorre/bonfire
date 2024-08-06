from flask import Blueprint, jsonify, request
from config import db
from models import Profile, User, Advertiser, AuthToken
from schemas import user_schema
from datetime import datetime, timezone
from .utils import hash_sha1, hash_secret, set_auth_token, verify_secret

profile = Blueprint("profile", __name__, url_prefix="/profile")

@profile.route("/signup", methods=["POST"])
def signup():
	req = request.get_json()
	handle = req.get("handle")
	pwd = req.get("password")
	is_adv = req.get("is_adv")
	profile = db.session.query(Profile).where(Profile.handle == handle).first()

	if profile:
		return jsonify({"error": "This username already exists"})
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
def login():
	req = request.get_json()
	handle = req.get("handle")
	pwd = req.get("password")
	profile = db.session.query(Profile).where(Profile.handle == handle).first()

	if profile:
		if verify_secret(pwd, profile.password):
			if db.session.query(Advertiser).where(Advertiser.id == profile.id).first():
				res = jsonify({"error": None, "is_adv": True})
			else:
				res = jsonify({"error": None, "is_adv": False})
		else:
			return jsonify({"error": "Wrong password"})
	else:
		return jsonify({"error": "User not found"})
	set_auth_token(profile, res)
	return res



@profile.route("/logout", methods=["GET"])
def logout():
	if ("auth_token" in request.cookies):
		db.session.query(AuthToken).where(AuthToken.value == hash_sha1(str(request.cookies.get("auth_token")))).delete()
		db.session.commit()
		res = jsonify({"error": None})
		res.set_cookie("auth_token", "", expires=0)
		return res
	return jsonify({"error": "Invalid token"})



@profile.route("/", methods=["GET"])
def get_token():
	if ("auth_token" in request.cookies):
		token = db.session.query(AuthToken).where(AuthToken.value == hash_sha1(str(request.cookies.get("auth_token"))), AuthToken.expiration_date > datetime.now(timezone.utc)).first()
		if token:
			if db.session.query(Advertiser).where(Advertiser.id == token.profile_id).first():
				return jsonify({"error": None, "id": token.profile_id, "is_adv": True})
			return jsonify({"id": token.profile_id, "is_adv": False, "error": None})
	return jsonify({"error": "Invalid token"})



@profile.route("/delete", methods=["POST"])
def delete_profiles():
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



@profile.route("/user", methods=["GET"])
def user():
	req = request.get_json()
	user_id = req.get("id")
	data = db.session.get(User, user_id)

	if not data:
		return jsonify({"error": "User not found"})
	return jsonify({"error": None, "data": user_schema.dump(data)})
