from flask import Blueprint, request
from config import db
from schemas import *
from models import *

api = Blueprint("api", __name__, url_prefix="/api")

@api.route("/profile", methods=["GET"])
def get_user():
	user_id = request.json["id"]
	data = db.session.get(User, user_id)
	if not data:
		return {"error": "User not found", "data": None}

	return {"error": None, "data": user_schema.dump(data)}

@api.route("/search", methods=["GET"])
def search_user():
	input_handle = request.json["query"]
	data = (db.session.query(User)
	.join(Profile)
	.filter(Profile.handle.contains(input_handle, autoescape=True))
	.all()
	)
	if not data:
		return {"error": "No users found", "data": None}

	return {"error": None, "data": id_username_schema.dump(data)}

@api.route("/login", methods=["POST"])
def login():
	handle = request.json["username"]
	password = request.json["password"]
	if (db.session.query(Profile).filter(Profile.handle==handle) and db.session.query(Profile).filter(Profile.password==hash(password))):
		# settare token
		return {"error": None, "data": "ok"}
	else:
		return {"error": "User not found", "data": None}


""""
@api.route("/create_user/<name>", methods=["GET"])
def create_user(name):
	new_profile = Profile(handle=name, password="1234", email=name+"@asdf.com")
	new_user = User(name=name, surname=name + "Fran", gender=GenderEnum.MALE, followers=0, following=0, profile=new_profile)
	db.session.add(new_profile)
	db.session.add(new_user)
	db.session.commit()
	return user_schema.dump(new_user)
"""