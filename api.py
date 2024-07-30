import bcrypt
import hashlib
from secrets import token_hex
from datetime import datetime, timedelta, timezone
from flask import Blueprint, Response, jsonify, request
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from config import db
from schemas import *
from models import *

api = Blueprint("api", __name__, url_prefix="/api")

def hash_secret(pwd: str) -> str:
	return bcrypt.hashpw(pwd.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

def verify_secret(pwd: str, stored_pwd: str) -> bool:
	return bcrypt.checkpw(pwd.encode("utf-8"), stored_pwd.encode("utf-8"))

def hash_md5(string: str) -> str:
	return hashlib.md5(string.encode('utf-8')).hexdigest()

def set_auth_token(profile: Profile, res: Response) -> None:
	token = token_hex(42)
	hashed_token = hash_md5(token)
	expiration_date = datetime.now(timezone.utc) + timedelta(weeks=1)

	while True:
		try:
			db.session.add(AuthToken(value=hashed_token, profile_id=profile.id, expiration_date=expiration_date))
			break
		except IntegrityError:
			db.session.rollback()
		token = token_hex(42)
		hashed_token = hash_md5(token)

	db.session.commit()

	res.set_cookie("auth_token", token, expires=expiration_date)

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
			new_profile = Profile(handle=handle, password=hash_secret(pwd))
			db.session.add(new_profile)
			db.session.commit()
			if is_adv:
				new_advertiser = Advertiser(id=new_profile.id)
				db.session.add(new_advertiser)
			else:
				new_user = User(id=new_profile.id, display_name=new_profile.handle)
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
		valid_tokens = db.session.query(AuthToken).filter(AuthToken.expiration_date > datetime.now(timezone.utc)).all()
		for token in valid_tokens:
			if hash_md5(request.cookies.get("auth_token")) == token.value:
				return jsonify({"error": None, "id": token.profile_id})
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
