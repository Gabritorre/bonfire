from flask import Blueprint, jsonify, request
from config import db, safeguard
from models import Comment, Profile, User, AuthToken, Like
from datetime import datetime, timezone
from .utils import hash_sha1

post = Blueprint("post", __name__, url_prefix="/post")

@post.route("/like", methods=["PUT"])
@safeguard
def like():
	if ("auth_token" in request.cookies):
		req = request.get_json()
		post_id = req.get("id")
		token = db.session.query(AuthToken).where(AuthToken.value == hash_sha1(str(request.cookies.get("auth_token"))), AuthToken.expiration_date > datetime.now(timezone.utc)).first()
		if token:
			user = db.session.query(User).where(User.id == token.profile_id).first()
			if user:
				like = db.session.query(Like).where(Like.user_id == user.id, Like.post_id == post_id).first()
				if like:
					like.liked = not like.liked
					db.session.commit()
					return jsonify({"error": None})
				else:
					db.session.add(Like(user_id=user.id, post_id=post_id, liked=True)) # first interaction with the post
					db.session.commit()
					return jsonify({"error": None})
	return jsonify({"error": "Invalid token"})



@post.route("/comment", methods=["PUT"])
@safeguard
def add_comment():
	if ("auth_token" in request.cookies):
		req = request.get_json()
		post_id = req.get("id")
		comment_body = req.get("body")
		token = db.session.query(AuthToken).where(AuthToken.value == hash_sha1(str(request.cookies.get("auth_token"))), AuthToken.expiration_date > datetime.now(timezone.utc)).first()
		if token:
			user = db.session.query(User).where(User.id == token.profile_id).first()
			if user:
				db.session.add(Comment(user_id=user.id, post_id=post_id, body=comment_body))
				db.session.commit()
				return jsonify({"error": None})
	return jsonify({"error": "Invalid token"})



@post.route("/comments", methods=["POST"])
@safeguard
def get_post_comments():
	if ("auth_token" in request.cookies):
		req = request.get_json()
		post_id = req.get("id")
		token = db.session.query(AuthToken).where(AuthToken.value == hash_sha1(str(request.cookies.get("auth_token"))), AuthToken.expiration_date > datetime.now(timezone.utc)).first()
		if token:
			comments = (db.session.query(Comment.id.label("comment_id"), User.id.label("user_id"), Profile.name, Comment.date, Comment.body, User.pfp)
						.join(User, Comment.user_id == User.id).join(Profile, Profile.id == User.id)
						.where(Comment.user_id == token.profile_id, Comment.post_id == post_id)
						.order_by(Comment.date)
						.all())
			return jsonify({
				"comments": [{"id": comment.comment_id, "user_id": comment.user_id, "name": comment.name, "date": comment.date.astimezone(timezone.utc).isoformat(), "body": comment.body, "pfp_url": comment.pfp} for comment in comments],
				"error": None
			})
	return jsonify({"error": "Invalid token"})
