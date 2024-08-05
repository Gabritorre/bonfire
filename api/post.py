from flask import Blueprint, jsonify, request
from config import db
from models import Post
from schemas import user_schema

post = Blueprint("post", __name__, url_prefix="/post")

@post.route("/like", methods=["POST"])
def user():
	req = request.get_json()
	post_id = req.get("id")
	data = db.session.get(Post, post_id)
	if not data:
		return jsonify({"error": "Post not found"})
	return jsonify({"error": None, "data": user_schema.dump(data)})
