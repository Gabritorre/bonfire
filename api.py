from flask import Blueprint
from config import db
from schemes import *
from models import *

api = Blueprint("user", __name__, url_prefix="/api")

@api.route("/user/<name>", methods=["GET"])
def get_user(name):

	new_profile = Profile(password="1234", email="gigi123@asdf.com")
	new_user = User(user_handle="myhandle", name=name, surname=name + "Franchetti", gender=GenderEnum.MALE, followers=0, following=0, profile=new_profile)
	db.session.add(new_profile)
	db.session.add(new_user)
	db.session.commit()
	return user_schema.dump(new_user)
