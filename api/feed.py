from datetime import timezone
from flask import Blueprint, jsonify, request
from sqlalchemy import select
from .utils import *
from config import db

feed = Blueprint("feed", __name__, url_prefix="/feed")

@feed.route("/explore", methods=["GET"])
def get_explore_posts():
	#todo: adjust offset if a post is deleted or a new post is added
	#todo: add an advertisement post every x posts
	req = request.get_json()
	page = req.get("page", 1)
	posts = db.session.query(Post).order_by(Post.date.desc()).limit(2).offset((page-1)*2)
	data = posts_schema.dump(posts)
	if ("auth_token" in request.cookies):
		stmt = select(AuthToken).where(AuthToken.value == hash_sha1(str(request.cookies.get("auth_token"))), AuthToken.expiration_date > datetime.now(timezone.utc))
		token = db.session.execute(stmt).scalar_one_or_none()
		if token:
			for count, post in enumerate(posts):
				data[count]['user_like'] = bool(db.session.query(UserInteraction).filter(UserInteraction.post_id == post.id, UserInteraction.user_id == token.profile_id, UserInteraction.liked == True).count())
	return jsonify({"error": None, "data": data})
