from flask import Blueprint, jsonify, request
from config import db
from models import Post, UserInteraction, AuthToken, Following
from schemas import posts_schema
from datetime import timezone, datetime
from .utils import hash_sha1

feed = Blueprint("feed", __name__, url_prefix="/feed")

POSTS_PER_CHUNK = 2

@feed.route("/explore", methods=["GET"])
def explore():
	#todo: add an advertisement post every x posts
	if ("auth_token" in request.cookies):
		token = db.session.query(AuthToken).where(AuthToken.value == hash_sha1(str(request.cookies.get("auth_token"))), AuthToken.expiration_date > datetime.now(timezone.utc)).first()
		if token:
			req = request.get_json()
			last_post_id = req.get("last_post_id")
			if last_post_id:
				posts = db.session.query(Post).where(Post.id < last_post_id).order_by(Post.id.desc())
			else:
				posts = db.session.query(Post).order_by(Post.id.desc())
			posts = posts.limit(POSTS_PER_CHUNK)
			data = posts_schema.dump(posts)

			# for each post check if the user liked it or not
			for count, post in enumerate(posts):
				data[count]['user_like'] = bool(db.session.query(UserInteraction).filter(UserInteraction.post_id == post.id, UserInteraction.user_id == token.profile_id, UserInteraction.liked == True).count())
			
			return jsonify({"error": None, "data": data})
	return jsonify({"error": "Invalid token"})


@feed.route("/friends", methods=["GET"])
def friends_posts():
	if ("auth_token" in request.cookies):
		token = db.session.query(AuthToken).where(AuthToken.value == hash_sha1(str(request.cookies.get("auth_token"))), AuthToken.expiration_date > datetime.now(timezone.utc)).first()
		if token:
			followings = db.session.query(Following).where(Following.follower == token.profile_id).all()
			friends_ids = [following.followed for following in followings]
			
			req = request.get_json()
			last_post_id = req.get("last_post_id")
			if last_post_id:
				posts = db.session.query(Post).where(Post.user_id.in_(friends_ids), Post.id < last_post_id).order_by(Post.id.desc())
			else:
				posts = db.session.query(Post).where(Post.user_id.in_(friends_ids)).order_by(Post.id.desc())
			posts = posts.limit(POSTS_PER_CHUNK)
			data = posts_schema.dump(posts)

			# for each post check if the user liked it or not
			for count, post in enumerate(posts):
				data[count]['user_like'] = bool(db.session.query(UserInteraction).filter(UserInteraction.post_id == post.id, UserInteraction.user_id == token.profile_id, UserInteraction.liked == True).count())
			
			return jsonify({"error": None, "data": data})
	return jsonify({"error": "Invalid token"})