from flask import Blueprint, jsonify, request
from config import db, safeguard
from models import Post, Following, User, PostTag, Tag
from schemas import posts_schema, ad_schema
from .utils import get_auth_token, recommend_ad, set_user_like, set_likes_count, set_comments_count

feed = Blueprint("feed", __name__, url_prefix="/feed")

POSTS_PER_CHUNK = 10

# Get a list of posts for the explore page
@feed.route("/explore", methods=["POST"])
@safeguard
def explore():
	token = get_auth_token(request.cookies)
	req = request.get_json()
	last_post_id = req["last_post_id"]
	if last_post_id:
		posts = db.session.query(Post).where(Post.id < last_post_id).order_by(Post.id.desc()) # get posts older than the last post in the previous chunk
	else:
		posts = db.session.query(Post).order_by(Post.id.desc())
	posts = posts.limit(POSTS_PER_CHUNK)

	posts_data = posts_schema.dump(posts)

	set_likes_count(posts, posts_data) # set the number of likes for each post
	set_comments_count(posts, posts_data) # set the number of comments for each post

	ad_data = None
	if posts_data:
		if token:
			set_user_like(posts, posts_data, token.profile_id) # for each post check if the current user liked it or not
			recommended_ad = recommend_ad(user_id=token.profile_id)
		else:
			recommended_ad = recommend_ad(user_id=None)

		if recommended_ad:
			db.session.flush()
			ad_data = ad_schema.dump(recommended_ad)
	return jsonify({"error": None, "posts": posts_data, "ad": ad_data})


# Get a list of posts from the user's friends
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
		posts = db.session.query(Post).where(Post.user_id.in_(friends_ids), Post.id < last_post_id).order_by(Post.id.desc()) # get posts older than the last post in the previous chunk
	else:
		posts = db.session.query(Post).where(Post.user_id.in_(friends_ids)).order_by(Post.id.desc())
	posts = posts.limit(POSTS_PER_CHUNK)
	posts_data = posts_schema.dump(posts)


	set_user_like(posts, posts_data, token.profile_id)	# for each post check if the current user liked it or not
	set_likes_count(posts, posts_data)	# set the number of likes for each post
	set_comments_count(posts, posts_data)	# set the number of comments for each post

	ad_data = None
	if posts_data:
		recommended_ad = recommend_ad(user_id=token.profile_id)
		if recommended_ad:
			ad_data = ad_schema.dump(recommended_ad)

	return jsonify({"error": None, "posts": posts_data, "ad": ad_data})


# Get a list of posts from a specific user
@feed.route("/user", methods=["POST"])
@safeguard
def user_posts():
	token = get_auth_token(request.cookies)
	req = request.get_json()
	user_id = req["id"]
	last_post_id = req["last_post_id"]

	if not db.session.query(User).where(User.id == user_id).first():
		return jsonify({"error": "User not found"})
	if last_post_id:
		posts = db.session.query(Post).where(Post.user_id == user_id, Post.id < last_post_id).order_by(Post.id.desc())	# get posts older than the last post in the previous chunk
	else:
		posts = db.session.query(Post).where(Post.user_id == user_id).order_by(Post.id.desc())
	posts = posts.limit(POSTS_PER_CHUNK)
	posts_data = posts_schema.dump(posts)

	set_likes_count(posts, posts_data) # set the number of likes for each post
	set_comments_count(posts, posts_data) # set the number of comments for each post

	if token:
		set_user_like(posts, posts_data, token.profile_id)	# for each post check if the current user liked it or not

	return jsonify({"error": None, "posts": posts_data})

# Get a list of posts with a specific tag
@feed.route("/tag", methods=["POST"])
@safeguard
def search_posts_by_tag():
	token = get_auth_token(request.cookies)
	req = request.get_json()
	input_tag = req["tag"]
	last_post_id = req["last_post_id"]

	tag = db.session.query(Tag).where(Tag.tag == input_tag).first()
	if not tag:
		return jsonify({"error": None, "posts": []})

	if last_post_id:
		posts = (db.session.query(Post)		# get posts older than the last post in the previous chunk
			.join(PostTag, Post.id == PostTag.post_id)
			.where(PostTag.tag_id == tag.id, Post.id < last_post_id)
			.order_by(Post.id.desc()))
	else:
		posts = db.session.query(Post).join(PostTag, Post.id == PostTag.post_id).where(PostTag.tag_id == tag.id).order_by(Post.id.desc())
	posts = posts.limit(POSTS_PER_CHUNK)
	posts_data = posts_schema.dump(posts)

	set_likes_count(posts, posts_data) # set the number of likes for each post
	set_comments_count(posts, posts_data) # set the number of comments for each post

	# for each post check if the user liked it or not
	if token:
		set_user_like(posts, posts_data, token.profile_id)	# for each post check if the current user liked it or not

	return jsonify({"error": None, "posts": posts_data})
