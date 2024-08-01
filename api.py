import bcrypt
import hashlib
from datetime import datetime, timedelta, timezone
from flask import Blueprint, Response, jsonify, request
from sqlalchemy import select, update
from sqlalchemy.exc import SQLAlchemyError
from config import db, Snowflake
from schemas import *
from models import *

api = Blueprint("api", __name__, url_prefix="/api")

def hash_secret(pwd: str) -> str:
	return bcrypt.hashpw(pwd.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

def verify_secret(pwd: str, stored_pwd: str) -> bool:
	return bcrypt.checkpw(pwd.encode("utf-8"), stored_pwd.encode("utf-8"))

def hash_md5(string: str) -> str:
	return hashlib.sha1(string.encode('utf-8')).hexdigest()

def set_auth_token(profile: Profile, res: Response) -> None:
	snowflake = Snowflake()

	sf = snowflake.generate()

	hashed_random_snowflake = hash_md5(f"{sf}")
	expiration_date = snowflake.creation_date(sf) + timedelta(weeks=1)

	db.session.add(AuthToken(value=hashed_random_snowflake, profile_id=profile.id, expiration_date=expiration_date))
	db.session.commit()

	res.set_cookie("auth_token", str(sf), expires=expiration_date)



@api.route("/profile", methods=["GET"])
def get_user():
	req = request.get_json()
	user_id = req.get("id")
	data = db.session.get(User, user_id)
	if not data:
		return jsonify({"error": "User not found", "data": None})
	return jsonify({"error": None, "data": user_schema.dump(data)})



@api.route("/search", methods=["GET"])
def search_user():
	req = request.get_json()
	input_handle = req.get("query")
	data = (db.session.query(User)
		.join(Profile)
		.filter(Profile.handle.contains(input_handle, autoescape=True))
		.all()
	)
	if not data:
		return jsonify({"error": "No users found", "data": None})
	return jsonify({"error": None, "data": id_username_schema.dump(data)})



@api.route("/signup", methods=["POST"])
def signup():
	req = request.get_json()
	handle = req.get("handle")
	pwd = req.get("password")
	confirm_pwd = req.get("confirm_password")
	is_adv = req.get("is_adv")

	stmt = select(Profile).where(Profile.handle == handle)
	profile = db.session.execute(stmt).scalar_one_or_none()
	if profile:
		return jsonify({"error": "This username already exists", "data": None})
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
			res = jsonify({"error": None, "data": "Ok"})
			set_auth_token(new_profile, res)
			return res

		else:
			return jsonify({"error": "Passwords do not match", "data": None})



@api.route("/login", methods=["POST"])
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
				res = jsonify({"error": None, "data": "Ok", "is_adv": True})
			else:
				res = jsonify({"error": None, "data": "Ok", "is_adv": False})
		else:
			return jsonify({"error": "Wrong password", "data": None, "is_adv": None})
	else:
		return jsonify({"error": "User not found", "data": None, "is_adv": None})


	set_auth_token(profile, res)
	return res


@api.route("/self", methods=["GET"])
def get_user_token():
	if ("auth_token" in request.cookies):
		stmt = select(AuthToken).where(AuthToken.value == hash_md5(str(request.cookies.get("auth_token"))), AuthToken.expiration_date > datetime.now(timezone.utc))
		token = db.session.execute(stmt).scalar_one_or_none()
		if token:
			stmt = select(Advertiser).where(Advertiser.id == token.profile_id)
			if db.session.execute(stmt).scalar_one_or_none():
				return jsonify({"error": None, "id": token.profile_id, "is_adv": True})
			return jsonify({"error": None, "id": token.profile_id, "is_adv": False})
	return jsonify({"error": "Invalid token"})


@api.route("/delete", methods=["POST"])
def delete_user():
	if ("auth_token" in request.cookies):
		stmt = select(AuthToken).where(AuthToken.value == hash_md5(str(request.cookies.get("auth_token"))), AuthToken.expiration_date > datetime.now(timezone.utc))
		token = db.session.execute(stmt).scalar_one_or_none()
		if token:
			try:
				user = db.session.get(User, token.profile_id)
				if user:
					db.session.delete(user)

				advertiser = db.session.get(Advertiser, token.profile_id)
				if advertiser:
					db.session.delete(advertiser)

				profile = db.session.get(Profile, token.profile_id)
				if profile:
					db.session.delete(profile)

				stmt = update(AuthToken).where(AuthToken.value == hash_md5(str(request.cookies.get("auth_token")))).values(expiration_date=datetime.now(timezone.utc) - timedelta(days=2))
				db.session.execute(stmt)

			except SQLAlchemyError as e:
				print("Error on /delete api")
				print(e)
				db.session.rollback()
				return jsonify({"error": "An error occured while deleting the user"})

			db.session.commit()
			return jsonify({"error": None})
	return jsonify({"error": "Invalid token"})

"""
@api.route("/create_user/<name>", methods=["GET"])
def create_user(name):
	new_profile = Profile(handle=name, password="1234", email=name+"@asdf.com")
	new_user = User(name=name, surname=name + "Fran", gender=GenderEnum.MALE, followers=0, following=0, profile=new_profile)
	db.session.add(new_profile)
	db.session.add(new_user)
	db.session.commit()
	return user_schema.dump(new_user)
"""
