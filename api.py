from flask import Blueprint, request
from config import db
from schemes import *
from models import *

api = Blueprint("api", __name__, url_prefix="/api")

@api.route("/profile", methods=["GET"])
def get_user():
	user_id = request.json["id"]
	data = db.session.get(User, user_id)
	if not data:
		return {"error": "User not found", "data": None}
	
	return {"error": None, "data": user_schema.dump(data)}

@api.route("/profile/picture", methods=["GET"])
def get_user_picture():
	user_id = request.json["id"]
	data = db.session.get(User, user_id)
	if not data:
		return {"error": "User not found", "data": None}
	
	return {"error": None, "data": {"pfp": user_schema.dump(data)["pfp"]}}

@api.route("/search", methods=["GET"])
def search_user():
	user_handle = request.json["query"]
	data = db.session.query(User).filter(User.user_handle.like("%{}%".format(user_handle))).all()
	if not data:
		return {"error": "No users found", "data": None}
	
	return {"error": None, "data": id_username_schema.dump(data)}

"""
@api.route("/create_user/<name>", methods=["GET"])
def create_user(name):
	new_profile = Profile(password="1234", email="oloui@asdf.com")
	new_user = User(user_handle="gigino", name=name, surname=name + "Fran", gender=GenderEnum.MALE, followers=0, following=0, profile=new_profile)
	db.session.add(new_profile)
	db.session.add(new_user)
	db.session.commit()
	return user_schema.dump(new_user)
"""