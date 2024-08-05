from flask import Blueprint, jsonify, request
from config import db
from models import Profile, User, Tag
from schemas import tags_schema, id_username_schema
from .settings import settings
from .user import user
from .profile import profile
from .feed import feed

api = Blueprint("api", __name__, url_prefix="/api")
api.register_blueprint(user)
api.register_blueprint(settings)
api.register_blueprint(profile)
api.register_blueprint(feed)

@api.route("/search", methods=["GET"])
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


@api.route("/tags", methods=["GET"])
def get_tags():
	tags = db.session.query(Tag).all()
	return jsonify({"error": None, "data": tags_schema.dump(tags)})
