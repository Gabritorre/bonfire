from flask import Blueprint, jsonify

api = Blueprint("api", __name__, url_prefix="/api")

@api.route("/feed")
def feed():
	return jsonify(["Post1", "Post2"])
