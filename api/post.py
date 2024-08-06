from flask import Blueprint, jsonify, request
from config import db
from models import User, Post, AuthToken, UserInteraction
from datetime import datetime, timezone
from .utils import hash_sha1

post = Blueprint("post", __name__, url_prefix="/post")

@post.route("/like", methods=["POST"])
def like():
	if ("auth_token" in request.cookies):
		req = request.get_json()
		post_id = req.get("id")
		token = db.session.query(AuthToken).where(AuthToken.value == hash_sha1(str(request.cookies.get("auth_token"))), AuthToken.expiration_date > datetime.now(timezone.utc)).first()
		if token:
			user = db.session.query(User).where(User.id == token.profile_id).first()
			if user:
				interaction = db.session.query(UserInteraction).where(UserInteraction.user_id == user.id, UserInteraction.post_id == post_id).first()
				if interaction:
					interaction.liked = not interaction.liked
					db.session.commit()
					return jsonify({"error": None})
				else:
					db.session.add(UserInteraction(user_id=user.id, post_id=post_id, liked=True)) # first interaction with the post
					db.session.commit()
					return jsonify({"error": None})
	return jsonify({"error": "Invalid token"})
