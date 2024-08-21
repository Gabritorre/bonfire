import json
from flask import Blueprint, jsonify, request
from config import db, safeguard
from models import BODY_LENGTH, Comment, Post, PostTag, User, Like
from schemas import post_schema, comments_schema
from .utils import delete_file, get_auth_token, update_interests, save_file, MAX_FILE_SIZE

post = Blueprint("post", __name__, url_prefix="/post")

# Create a new post for the current user
@post.route("/", methods=["PUT"])
@safeguard
def create_post():
	token = get_auth_token(request.cookies)
	if not token:
		return jsonify({"error": "Invalid token"})

	req = json.loads(request.form["json"])
	body = req["body"]
	tags = req["tags"]
	media = request.files.get("media")

	if len(body) > BODY_LENGTH:
		return jsonify({"error": "Post body is too long"})

	filename = None
	if media:
		if len(media.read()) > MAX_FILE_SIZE:
			return jsonify({"error": "File too large"})
		media.seek(0)
		filename = save_file(media)

	try:
		post = Post(user_id=token.profile_id, body=body, media=filename)
		db.session.add(post)
		db.session.flush()
		for tag in tags:
			db.session.add(PostTag(post_id=post.id, tag_id=tag))
		db.session.flush()
	except:
		if filename:
			delete_file(filename)
		raise

	post_data = post_schema.dump(post)
	post_data["likes"] = 0
	post_data["comments"] = 0
	post_data["user_like"] = False

	return jsonify({"error": None, "post": post_data})



# Delete a post owned by the current user
@post.route("/", methods=["DELETE"])
@safeguard
def delete_post():
	token = get_auth_token(request.cookies)
	if not token:
		return jsonify({"error": "Invalid token"})

	req = request.get_json()
	post_id = req["id"]
	post = db.session.query(Post).where(Post.id==post_id, Post.user_id==token.profile_id).first()
	if not post:
		return jsonify({"error": "Post not found"})
	db.session.delete(post)
	if post.media:
		delete_file(post.media)
	db.session.flush()
	return jsonify({"error": None})



# Add a like to a post, increasing the user's interest in the post's tags
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
		update_interests(token.profile_id, post_id, inc=0.2, dec=-0.1)
		db.session.flush()
		return jsonify({"error": None})
	else:
		return jsonify({"error": "User not found"})


# Remove a like from a post
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
		update_interests(token.profile_id, post_id, inc=-0.2, dec=0.1)
		db.session.flush()
		return jsonify({"error": None})
	else:
		return jsonify({"error": "User not found"})



# Add a comment to a post, increasing the user's interest in the post's tags
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
		update_interests(token.profile_id, post_id, inc=0.4, dec=-0.1)
		db.session.flush()
		return jsonify({"error": None})
	else:
		return jsonify({"error": "User not found"})



# Remove a comment from a post, only the comment's owner can delete it
@post.route("/comment", methods=["DELETE"])
@safeguard
def delete_comment():
	token = get_auth_token(request.cookies)

	req = request.get_json()
	comment_id = req["id"]
	comment = db.session.query(Comment).where(Comment.id == comment_id).first()
	if not comment:
		return jsonify({"error": "Comment not found"})
	if not token or comment.user_id != token.profile_id:
		return jsonify({"error": "Comment doesn't belong to this user"})
	db.session.delete(comment)
	update_interests(token.profile_id, comment.post_id, inc=-0.4, dec=0.1)
	db.session.flush()
	return jsonify({"error": None})



# Get all the comments for a post
@post.route("/comments", methods=["POST"])
@safeguard
def get_post_comments():
	req = request.get_json()
	post_id = req["id"]

	if not db.session.query(Post).where(Post.id == post_id).first():
		return jsonify({"error": "Post not found"})

	comments = db.session.query(Comment).where(Comment.post_id == post_id).order_by(Comment.date).all()
	return jsonify({"error": None, "comments": comments_schema.dump(comments)})
