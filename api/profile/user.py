from flask import Blueprint, jsonify, request
from config import db, safeguard
from models import Following, User, Profile
from schemas import user_schema, id_username_schema
from api.utils import get_auth_token

user = Blueprint("user", __name__, url_prefix="/user")

# Get info about a user, including "handle", "name", "creation_date", "gender", "pfp", "biography", "birthday", "follower", "following", "interests"
@user.route("/", methods=["POST"])
@safeguard
def get_user():
	token = get_auth_token(request.cookies)
	req = request.get_json()
	user_id = req["id"]
	user = db.session.get(User, user_id)

	if not user:
		return jsonify({"error": "User not found"})

	# Check if the current user follows the selected user
	user_data = user_schema.dump(user)
	if token:
		user_data["followed"] = bool(db.session.query(Following).where(Following.follower == token.profile_id, Following.followed == user_id).count())
	return jsonify({"error": None, "user": user_data})



# Search for users by handle, retuns a list of users with "id", "pfp", "handle", "name"
@user.route("/search", methods=["POST"])
@safeguard
def search_user():
	req = request.get_json()
	input_handle = req["query"]
	data = (db.session.query(User)
		.join(Profile)
		.where(Profile.handle.contains(input_handle, autoescape=True))
		.all()
	)
	if not data:
		return jsonify({"error": "No users found"})
	return jsonify({"error": None, "data": id_username_schema.dump(data)})



# Make the current user follow a user defined by their "id"
@user.route("/follow", methods=["PUT"])
@safeguard
def follow():
	token = get_auth_token(request.cookies)
	if not token:
		return jsonify({"error": "Invalid token"})

	req = request.get_json()
	to_follow_id = req["id"]
	if db.session.get(User, to_follow_id):
		user = db.session.query(User).where(User.id == token.profile_id).first()
		if user and user.id != to_follow_id:
			db.session.add(Following(follower=user.id, followed=to_follow_id))
			db.session.commit()
			return jsonify({"error": None})
		else:
			return jsonify({"error": "Cannot self follow"})
	else:
		return jsonify({"error": "User not found"})



# Make the current user unfollow a user defined by their "id"
@user.route("/follow", methods=["DELETE"])
@safeguard
def unfollow():
	token = get_auth_token(request.cookies)
	if not token:
		return jsonify({"error": "Invalid token"})

	req = request.get_json()
	to_unfollow_id = req["id"]
	if db.session.get(User, to_unfollow_id):
		user = db.session.query(User).where(User.id == token.profile_id).first()
		if user:
			db.session.query(Following).where(Following.follower==user.id, Following.followed==to_unfollow_id).delete()
			db.session.commit()
			return jsonify({"error": None})
		else:
			return jsonify({"error": "User not found"})
	else:
		return jsonify({"error": "User not found"})



# Get a list of users that follow the user defined by their "id"
@user.route("/followers", methods=["POST"])
@safeguard
def get_followers():
	req = request.get_json()
	user_id = req["id"]

	followers = db.session.query(User).join(Following, Following.follower == User.id).where(Following.followed == user_id).all()

	return jsonify({"error": None, "followers" : id_username_schema.dump(followers)})



# Get a list of users that the user defined by their "id" follows
@user.route("/followed", methods=["POST"])
@safeguard
def get_followed():
	req = request.get_json()
	user_id = req["id"]

	followed = db.session.query(User).join(Following, Following.followed == User.id).where(Following.follower == user_id).all()

	return jsonify({"error": None, "followed": id_username_schema.dump(followed)})
