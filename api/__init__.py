from flask import Blueprint, jsonify
from models import Tag
from schemas import tags_schema
from config import db, safeguard
from .profile import profile
from .settings import settings
from .feed import feed
from .post import post
from .ad import ad

api = Blueprint("api", __name__, url_prefix="/api")
api.register_blueprint(profile)
api.register_blueprint(settings)
api.register_blueprint(feed)
api.register_blueprint(post)
api.register_blueprint(ad)


# Get a list of all tags
@api.route("/tags", methods=["GET"])
@safeguard
def get_all_tags():
	tags = db.session.query(Tag).all()
	return jsonify({"error": None, "tags": tags_schema.dump(tags)})
