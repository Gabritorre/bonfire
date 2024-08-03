import bcrypt
import hashlib
from datetime import datetime, timedelta, timezone
from flask import Blueprint, Response, jsonify, request
from sqlalchemy import select, update, delete, insert
from sqlalchemy.exc import SQLAlchemyError
from config import db, snowflake
from schemas import *
from models import *

api = Blueprint("api", __name__, url_prefix="/api")

def hash_secret(pwd: str) -> str:
	return bcrypt.hashpw(pwd.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

def verify_secret(pwd: str, stored_pwd: str) -> bool:
	return bcrypt.checkpw(pwd.encode("utf-8"), stored_pwd.encode("utf-8"))

def hash_sha1(string: str) -> str:
	return hashlib.sha1(string.encode("utf-8")).hexdigest()

def set_auth_token(profile: Profile, res: Response) -> None:
	sf = snowflake.generate()

	hashed_sf = hash_sha1(f"{sf}")
	expiration_date = snowflake.creation_date(sf) + timedelta(weeks=1)

	db.session.add(AuthToken(value=hashed_sf, profile_id=profile.id, expiration_date=expiration_date))
	db.session.commit()

	res.set_cookie("auth_token", str(sf), expires=expiration_date)



@api.route("/profile", methods=["GET"])
def get_user():
	req = request.get_json()
	user_id = req.get("id")
	data = db.session.get(User, user_id)
	if not data:
		return jsonify({"error": "User not found"})
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
		return jsonify({"error": "No users found"})
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
				res = jsonify({"error": None, "is_adv": True})
			else:
				res = jsonify({"error": None, "is_adv": False})
		else:
			return jsonify({"error": "Wrong password"})
	else:
		return jsonify({"error": "User not found"})


	set_auth_token(profile, res)
	return res

@api.route("/logout", methods=["GET"])
def logout():
	if ("auth_token" in request.cookies):
		stmt = delete(AuthToken).where(AuthToken.value == hash_sha1(str(request.cookies.get("auth_token"))))
		db.session.execute(stmt)
		db.session.commit()
		res = jsonify({"error": None})
		res.set_cookie("auth_token", "", expires=0)
		return res
	return jsonify({"error": "Invalid token"})

@api.route("/self", methods=["GET"])
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


@api.route("/delete", methods=["POST"])
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


@api.route("/tags", methods=["GET"])
def get_tags():
	tags = db.session.query(Tag).all()
	return jsonify({"error": None, "data": tags_schema.dump(tags)})


@api.route("settings/user", methods=["GET"])
def get_user_settings():
	if ("auth_token" in request.cookies):
		stmt = select(AuthToken).where(AuthToken.value == hash_sha1(str(request.cookies.get("auth_token"))), AuthToken.expiration_date > datetime.now(timezone.utc))
		token = db.session.execute(stmt).scalar_one_or_none()
		if token:
			stmt = select(User).where(User.id == token.profile_id)
			profile = db.session.execute(stmt).scalar_one_or_none()
			if profile:
				return jsonify({"error": None, "data": user_settings_schema.dump(profile)})
	return jsonify({"error": "Invalid token"})

@api.route("settings/user", methods=["POST"])
def set_user_settings():
	if ("auth_token" in request.cookies):
		stmt = select(AuthToken).where(AuthToken.value == hash_sha1(str(request.cookies.get("auth_token"))), AuthToken.expiration_date > datetime.now(timezone.utc))
		token = db.session.execute(stmt).scalar_one_or_none()
		if token:
			req = request.get_json()
			new_display_name = req.get("display_name", None)
			new_gender = req.get("gender", None)
			new_biography = req.get("biography", None)
			new_birthdate = req.get("birthday", None)
			new_password = req.get("password", None)
			if new_display_name:
				stmt = update(Profile).where(Profile.id == token.profile_id).values(name=new_display_name)
				db.session.execute(stmt)
			if new_gender == "male" or new_gender =="female" or new_gender == "other":
				stmt = update(User).where(User.id == token.profile_id).values(gender=new_gender)
				db.session.execute(stmt)
			if new_biography:
				stmt = update(User).where(User.id == token.profile_id).values(biography=new_biography)
				db.session.execute(stmt)
			if new_birthdate and datetime.strptime(new_birthdate, DATE_FORMAT) < datetime.now():
				stmt = update(User).where(User.id == token.profile_id).values(birthday=datetime.strptime(new_birthdate, DATE_FORMAT))
				db.session.execute(stmt)
			if new_password:
				stmt = update(Profile).where(Profile.id == token.profile_id).values(password=hash_secret(new_password))
				db.session.execute(stmt)

			current_interests = db.session.query(Interest).filter(Interest.user_id == token.profile_id).all()
			current_interests_ids = {interest.tag_id for interest in current_interests}
			new_interests = set(req.get("interests", set()))
			interests_to_remove = current_interests_ids - new_interests
			interests_to_add = new_interests - current_interests_ids

			if interests_to_remove:
				stmt = delete(Interest).where(Interest.user_id == token.profile_id, Interest.tag_id.in_(interests_to_remove))
				db.session.execute(stmt)
			if interests_to_add:
				for interest in interests_to_add:
					stmt = insert(Interest).values(user_id=token.profile_id, tag_id=interest, interest=1.0)
					db.session.execute(stmt)

			db.session.commit()
			return jsonify({"error": None})
	return jsonify({"error": "Invalid token"})

@api.route("/feed/explore", methods=["GET"])
def get_explore_posts():
	#todo: adjust offset if a post is deleted or a new post is added
	#todo: add an advertisement post every x posts
	req = request.get_json()
	page = req.get("page", 1)
	posts = db.session.query(Post).order_by(Post.date.desc()).limit(2).offset((page-1)*2)
	data = posts_schema.dump(posts)
	if ("auth_token" in request.cookies):
		stmt = select(AuthToken).where(AuthToken.value == hash_sha1(str(request.cookies.get("auth_token"))), AuthToken.expiration_date > datetime.now(timezone.utc))
		token = db.session.execute(stmt).scalar_one_or_none()
		if token:
			for count, post in enumerate(posts):
				data[count]['user_like'] = bool(db.session.query(UserInteraction).filter(UserInteraction.post_id == post.id, UserInteraction.user_id == token.profile_id, UserInteraction.liked == True).count())
	return jsonify({"error": None, "data": data})


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
