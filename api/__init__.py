from flask import Blueprint, jsonify
from models import Tag
from schemas import tags_schema
from config import db
from .profile import profile
from .settings import settings
from .feed import feed
from .post import post
from .adv import adv

api = Blueprint("api", __name__, url_prefix="/api")
api.register_blueprint(profile)
api.register_blueprint(settings)
api.register_blueprint(feed)
api.register_blueprint(post)
api.register_blueprint(adv)

@api.route("/tags", methods=["GET"])
def get_all_tags():
	tags = db.session.query(Tag).all()
	return jsonify({"error": None, "data": tags_schema.dump(tags)})
