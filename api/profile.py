from flask import Blueprint, jsonify, request
from config import db
from models import User
from schemas import user_schema

profile = Blueprint("profile", __name__, url_prefix="/profile")

@profile.route("/user", methods=["GET"])
def user():
	req = request.get_json()
	user_id = req.get("id")
	data = db.session.get(User, user_id)

	if not data:
		return jsonify({"error": "User not found"})
	return jsonify({"error": None, "data": user_schema.dump(data)})
