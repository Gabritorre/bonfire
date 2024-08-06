from flask import Blueprint, jsonify, request
from config import db
from models import Following, Profile, User, Tag, AuthToken
from schemas import tags_schema, id_username_schema
from datetime import datetime, timezone
from .utils import hash_sha1

user = Blueprint("user", __name__, url_prefix="/user")

@user.route("/search", methods=["GET"])
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



@user.route("/tags", methods=["GET"])
def get_all_tags():
	tags = db.session.query(Tag).all()
	return jsonify({"error": None, "data": tags_schema.dump(tags)})



@user.route("/follow", methods=["POST"])
def follow():
	if ("auth_token" in request.cookies):
		token = db.session.query(AuthToken).where(AuthToken.value == hash_sha1(str(request.cookies.get("auth_token"))), AuthToken.expiration_date > datetime.now(timezone.utc)).first()
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
