from flask import Blueprint, jsonify, request
from config import db, safeguard
from models import Profile, User, Interest, AuthToken, DATE_FORMAT
from schemas import user_settings_schema
from datetime import datetime, timezone
from .utils import hash_sha1, hash_secret

settings = Blueprint("settings", __name__, url_prefix="/settings")

@settings.route("/user", methods=["GET"])
@safeguard
def get_user_settings():
	if ("auth_token" in request.cookies):
		token = db.session.query(AuthToken).where(AuthToken.value == hash_sha1(str(request.cookies.get("auth_token"))), AuthToken.expiration_date > datetime.now(timezone.utc)).first()
		if token:
			profile = db.session.query(User).where(User.id == token.profile_id).first()
			if profile:
				return jsonify({"error": None, "data": user_settings_schema.dump(profile)})
	return jsonify({"error": "Invalid token"})



@settings.route("/user", methods=["PUT"])
@safeguard
def set_user_settings():
	if ("auth_token" in request.cookies):
		token = db.session.query(AuthToken).where(AuthToken.value == hash_sha1(str(request.cookies.get("auth_token"))), AuthToken.expiration_date > datetime.now(timezone.utc)).first()
		if token:
			req = request.get_json()
			new_display_name = req.get("display_name")
			new_gender = req.get("gender")
			new_biography = req.get("biography")
			new_birthdate = req.get("birthday")
			new_password = req.get("password")
			new_interests = req.get("interests")

			if new_display_name:
				db.session.query(Profile).where(Profile.id == token.profile_id).update({"name": new_display_name})
			if new_gender in ["male", "female", "other"]:
				db.session.query(User).where(User.id == token.profile_id).update({"gender": new_gender})
			if new_biography:
				db.session.query(User).where(User.id == token.profile_id).update({"biography":new_biography})
			if new_birthdate and datetime.strptime(new_birthdate, DATE_FORMAT) < datetime.now():
				db.session.query(User).where(User.id == token.profile_id).update({"birthday": datetime.strptime(new_birthdate, DATE_FORMAT)})
			if new_password:
				db.session.query(Profile).where(Profile.id == token.profile_id).update({"password": hash_secret(new_password)})
			if new_interests:
				current_interests = db.session.query(Interest).where(Interest.user_id == token.profile_id).all()
				current_interests_ids = {interest.tag_id for interest in current_interests}
				new_interests = set(new_interests)
				interests_to_remove = current_interests_ids - new_interests
				interests_to_add = new_interests - current_interests_ids
				if interests_to_remove:
					db.session.query(Interest).where(Interest.user_id == token.profile_id, Interest.tag_id.in_(interests_to_remove)).delete()
				if interests_to_add:
					for interest in interests_to_add:
						db.session.add(Interest(user_id=token.profile_id, tag_id=interest, interest=1.0))

			db.session.commit()
			return jsonify({"error": None})
	return jsonify({"error": "Invalid token"})
