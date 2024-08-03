from datetime import datetime, timezone
from flask import Blueprint, jsonify, request
from sqlalchemy import select, delete
from sqlalchemy.exc import SQLAlchemyError
from config import db
from .utils import *

user = Blueprint("user", __name__, url_prefix="/user")

@user.route("/signup", methods=["POST"])
def signup():
	req = request.get_json()
	handle = req.get("handle")
	pwd = req.get("password")
	confirm_pwd = req.get("confirm_password")
	is_adv = req.get("is_adv")

	stmt = select(Profile).where(Profile.handle == handle)
	profile = db.session.execute(stmt).scalar_one_or_none()
	if profile:
		return jsonify({"error": "This username already exists"})
	else:
		if pwd == confirm_pwd:
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

		else:
			return jsonify({"error": "Passwords do not match"})



@user.route("/login", methods=["POST"])
def login():
	req = request.get_json()
	handle = req.get("handle")
	pwd = req.get("password")

	stmt = select(Profile).where(Profile.handle == handle)
	profile = db.session.execute(stmt).scalar_one_or_none()
	if profile:
		if verify_secret(pwd, profile.password):
			stmt = select(Advertiser).where(Advertiser.id == profile.id)
			if db.session.execute(stmt).scalar_one_or_none():
				res = jsonify({"error": None, "is_adv": True})
			else:
				res = jsonify({"error": None, "is_adv": False})
		else:
			return jsonify({"error": "Wrong password"})
	else:
		return jsonify({"error": "User not found"})


	set_auth_token(profile, res)
	return res



@user.route("/logout", methods=["GET"])
def logout():
	if ("auth_token" in request.cookies):
		stmt = delete(AuthToken).where(AuthToken.value == hash_sha1(str(request.cookies.get("auth_token"))))
		db.session.execute(stmt)
		db.session.commit()
		res = jsonify({"error": None})
		res.set_cookie("auth_token", "", expires=0)
		return res
	return jsonify({"error": "Invalid token"})



@user.route("/", methods=["GET"])
def get_user_token():
	if ("auth_token" in request.cookies):
		stmt = select(AuthToken).where(AuthToken.value == hash_sha1(str(request.cookies.get("auth_token"))), AuthToken.expiration_date > datetime.now(timezone.utc))
		token = db.session.execute(stmt).scalar_one_or_none()
		if token:
			stmt = select(Advertiser).where(Advertiser.id == token.profile_id)
			if db.session.execute(stmt).scalar_one_or_none():
				return jsonify({"error": None, "id": token.profile_id, "is_adv": True})
			return jsonify({"error": None, "id": token.profile_id, "is_adv": False})
	return jsonify({"error": "Invalid token"})



@user.route("/delete", methods=["POST"])
def delete_user():
	if ("auth_token" in request.cookies):
		stmt = select(AuthToken).where(AuthToken.value == hash_sha1(str(request.cookies.get("auth_token"))), AuthToken.expiration_date > datetime.now(timezone.utc))
		token = db.session.execute(stmt).scalar_one_or_none()
		if token:
			try:
				profile = db.session.get(Profile, token.profile_id)
				if profile:
					db.session.delete(profile)

				stmt = delete(AuthToken).where(AuthToken.profile_id == token.profile_id)
				db.session.execute(stmt)

			except SQLAlchemyError as e:
				print("Error on /delete api")
				print(e)
				db.session.rollback()
				return jsonify({"error": "An error occured while deleting the user"})

			db.session.commit()
			res = jsonify({"error": None})
			res.set_cookie("auth_token", "", expires=0)
			return res
	return jsonify({"error": "Invalid token"})
