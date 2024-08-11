from flask import Blueprint, jsonify, request
from config import db, safeguard
from models import Post, Following, Like
from schemas import posts_schema
from .utils import get_auth_token

feed = Blueprint("feed", __name__, url_prefix="/feed")

POSTS_PER_CHUNK = 2

@feed.route("/explore", methods=["POST"])
@safeguard
def explore():
	#todo: add an advertisement post every x posts
	req = request.get_json()
	last_post_id = req["last_post_id"]
	if last_post_id:
		posts = db.session.query(Post).where(Post.id < last_post_id).order_by(Post.id.desc())
	else:
		posts = db.session.query(Post).order_by(Post.id.desc())
	posts = posts.limit(POSTS_PER_CHUNK)
	data = posts_schema.dump(posts)

	# for each post check if the user liked it or not
	for count, post in enumerate(posts):
		data[count]['user_like'] = bool(db.session.query(Like).where(Like.post_id == post.id, Like.liked == True).count())

	return jsonify({"error": None, "data": data})



@feed.route("/friends", methods=["POST"])
@safeguard
def friends_posts():
	token = get_auth_token(request.cookies)
	if not token:
		return jsonify({"error": "Invalid token"})

	followings = db.session.query(Following).where(Following.follower == token.profile_id).all()
	friends_ids = [following.followed for following in followings]

	req = request.get_json()
	last_post_id = req["last_post_id"]
	if last_post_id:
		posts = db.session.query(Post).where(Post.user_id.in_(friends_ids), Post.id < last_post_id).order_by(Post.id.desc())
	else:
		posts = db.session.query(Post).where(Post.user_id.in_(friends_ids)).order_by(Post.id.desc())
	posts = posts.limit(POSTS_PER_CHUNK)
	data = posts_schema.dump(posts)

	# for each post check if the user liked it or not
	for count, post in enumerate(posts):
		data[count]['user_like'] = bool(db.session.query(Like).where(Like.post_id == post.id, Like.user_id == token.profile_id, Like.liked == True).count())

	return jsonify({"error": None, "data": data})
