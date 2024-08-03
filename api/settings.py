from datetime import datetime, timezone
from flask import Blueprint, jsonify, request
from sqlalchemy import select, update, delete, insert
from schemas import user_settings_schema
from .utils import *

settings = Blueprint("settings", __name__, url_prefix="/settings")

@settings.route("/user", methods=["GET"])
def get_user_settings():
	if ("auth_token" in request.cookies):
		stmt = select(AuthToken).where(AuthToken.value == hash_sha1(str(request.cookies.get("auth_token"))), AuthToken.expiration_date > datetime.now(timezone.utc))
		token = db.session.execute(stmt).scalar_one_or_none()
		if token:
			stmt = select(User).where(User.id == token.profile_id)
			profile = db.session.execute(stmt).scalar_one_or_none()
			if profile:
				return jsonify({"error": None, "data": user_settings_schema.dump(profile)})
	return jsonify({"error": "Invalid token"})



@settings.route("/user", methods=["POST"])
def set_user_settings():
	if ("auth_token" in request.cookies):
		stmt = select(AuthToken).where(AuthToken.value == hash_sha1(str(request.cookies.get("auth_token"))), AuthToken.expiration_date > datetime.now(timezone.utc))
		token = db.session.execute(stmt).scalar_one_or_none()
		if token:
			req = request.get_json()
			new_display_name = req.get("display_name", None)
			new_gender = req.get("gender", None)
			new_biography = req.get("biography", None)
			new_birthdate = req.get("birthday", None)
			new_password = req.get("password", None)
			if new_display_name:
				stmt = update(Profile).where(Profile.id == token.profile_id).values(name=new_display_name)
				db.session.execute(stmt)
			if new_gender == "male" or new_gender =="female" or new_gender == "other":
				stmt = update(User).where(User.id == token.profile_id).values(gender=new_gender)
				db.session.execute(stmt)
			if new_biography:
				stmt = update(User).where(User.id == token.profile_id).values(biography=new_biography)
				db.session.execute(stmt)
			if new_birthdate and datetime.strptime(new_birthdate, DATE_FORMAT) < datetime.now():
				stmt = update(User).where(User.id == token.profile_id).values(birthday=datetime.strptime(new_birthdate, DATE_FORMAT))
				db.session.execute(stmt)
			if new_password:
				stmt = update(Profile).where(Profile.id == token.profile_id).values(password=hash_secret(new_password))
				db.session.execute(stmt)

			current_interests = db.session.query(Interest).filter(Interest.user_id == token.profile_id).all()
			current_interests_ids = {interest.tag_id for interest in current_interests}
			new_interests = set(req.get("interests", set()))
			interests_to_remove = current_interests_ids - new_interests
			interests_to_add = new_interests - current_interests_ids

			if interests_to_remove:
				stmt = delete(Interest).where(Interest.user_id == token.profile_id, Interest.tag_id.in_(interests_to_remove))
				db.session.execute(stmt)
			if interests_to_add:
				for interest in interests_to_add:
					stmt = insert(Interest).values(user_id=token.profile_id, tag_id=interest, interest=1.0)
					db.session.execute(stmt)

			db.session.commit()
			return jsonify({"error": None})
	return jsonify({"error": "Invalid token"})
