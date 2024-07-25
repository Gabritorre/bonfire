from flask import Blueprint, jsonify

user = Blueprint("user", __name__, url_prefix="/api")

@user.route("/user/<name>", methods=["GET"])
def get_user(name):
	return jsonify({"id":1,"name": name})

