from flask import Blueprint, jsonify, request
from config import db, safeguard
from models import Following, User, AuthToken, Profile
from schemas import user_schema, id_username_schema
from datetime import datetime, timezone
from api.utils import hash_sha1

user = Blueprint("user", __name__, url_prefix="/user")

@user.route("/", methods=["POSt"])
@safeguard
def get_user():
	req = request.get_json()
	user_id = req.get("id")
	data = db.session.get(User, user_id)

	if not data:
		return jsonify({"error": "User not found"})
	return jsonify({"error": None, "data": user_schema.dump(data)})



@user.route("/search", methods=["POST"])
@safeguard
def search_user():
	req = request.get_json()
	input_handle = req.get("query")
	data = (db.session.query(User)
		.join(Profile)
		.where(Profile.handle.contains(input_handle, autoescape=True))
		.all()
	)
	if not data:
		return jsonify({"error": "No users found"})
	return jsonify({"error": None, "data": id_username_schema.dump(data)})



@user.route("/follow", methods=["PUT"])
@safeguard
def follow():
	if ("auth_token" in request.cookies):
		token = db.session.query(AuthToken).where(AuthToken.value == hash_sha1(str(request.cookies.get("auth_token"))), AuthToken.expiration_date > datetime.now(timezone.utc)).first()
		print(request.cookies.get("auth_token"), token)
		if token:
			req = request.get_json()
			to_follow_id = req.get("id")
			if db.session.get(User, to_follow_id):
				user = db.session.query(User).where(User.id == token.profile_id).first()
				if user:
					following_relationship = db.session.query(Following).where(Following.follower==user.id, Following.followed==to_follow_id).first()
					if following_relationship: # unfollow
						db.session.delete(following_relationship)
					else:
						db.session.add(Following(follower=user.id, followed=to_follow_id)) # follow
					db.session.commit()
				return jsonify({"error": None})
			else:
				return jsonify({"error": "User does not exist"})
	return jsonify({"error": "Invalid token"})
