from flask import Blueprint, jsonify, request
from config import db, safeguard
from models import Comment, Profile, User,Like
from datetime import timezone
from .utils import get_auth_token

post = Blueprint("post", __name__, url_prefix="/post")

@post.route("/like", methods=["PUT"])
@safeguard
def like():
	token = get_auth_token(request.cookies)
	if not token:
		return jsonify({"error": "Invalid token"})

	req = request.get_json()
	post_id = req["id"]
	user = db.session.query(User).where(User.id == token.profile_id).first()
	if user:
		db.session.add(Like(user_id=user.id, post_id=post_id))
		db.session.commit()
		return jsonify({"error": None})
	else:
		return jsonify({"error": "User not found"})



@post.route("/like", methods=["DELETE"])
@safeguard
def remove_like():
	token = get_auth_token(request.cookies)
	if not token:
		return jsonify({"error": "Invalid token"})

	req = request.get_json()
	post_id = req["id"]
	user = db.session.query(User).where(User.id == token.profile_id).first()
	if user:
		db.session.query(Like).where(Like.user_id == user.id, Like.post_id == post_id).delete()
		db.session.commit()
		return jsonify({"error": None})
	else:
		return jsonify({"error": "User not found"})



@post.route("/comment", methods=["PUT"])
@safeguard
def add_comment():
	token = get_auth_token(request.cookies)
	if not token:
		return jsonify({"error": "Invalid token"})

	req = request.get_json()
	post_id = req["id"]
	comment_body = req["body"]
	user = db.session.query(User).where(User.id == token.profile_id).first()
	if user:
		db.session.add(Comment(user_id=user.id, post_id=post_id, body=comment_body))
		db.session.commit()
		return jsonify({"error": None})
	else:
		return jsonify({"error": "User not found"})



@post.route("/comments", methods=["POST"])
@safeguard
def get_post_comments():
	req = request.get_json()
	post_id = req["id"]
	comments = (db.session.query(Comment.id.label("comment_id"), User.id.label("user_id"), Profile.handle, Profile.name, User.pfp, Comment.date, Comment.body)
				.join(User, Comment.user_id == User.id).join(Profile, Profile.id == User.id)
				.where(Comment.post_id == post_id)
				.order_by(Comment.date)
				.all())
	return jsonify({
		"comments": [{"id": comment.comment_id, "user_id": comment.user_id, "handle": comment.handle, "name": comment.name, "pfp": comment.pfp, "date": comment.date.astimezone(timezone.utc).isoformat(), "body": comment.body} for comment in comments],
		"error": None
	})
