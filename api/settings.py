import json
from flask import Blueprint, jsonify, request
from config import db, safeguard
from models import Profile, User, Advertiser, Interest, DATE_FORMAT
from schemas import user_settings_schema, adv_settings_schema
from datetime import datetime
from .utils import hash_secret, get_auth_token, save_file, delete_file, MAX_FILE_SIZE

settings = Blueprint("settings", __name__, url_prefix="/settings")

# Get the settings of the current user, indluding "name", "handle", "pfp", "gender", "biography", "birthday", "interests"
@settings.route("/user", methods=["GET"])
@safeguard
def get_user_settings():
	token = get_auth_token(request.cookies)
	if not token:
		return jsonify({"error": "Invalid token"})

	user = db.session.query(User).where(User.id == token.profile_id).first()
	if user:
		return jsonify({"error": None, "user": user_settings_schema.dump(user)})
	return jsonify({"error": "User not found"})



# Update the settings of the current user
@settings.route("/user", methods=["PUT"])
@safeguard
def set_user_settings():
	token = get_auth_token(request.cookies)
	if not token:
		return jsonify({"error": "Invalid token"})

	req = json.loads(request.form["json"])
	new_display_name = req["display_name"]
	new_gender = req["gender"]
	new_biography = req["biography"]
	new_birthday = req["birthday"]
	new_password = req["password"]
	new_interests = req["interests"]
	pfp = request.files.get("pfp")

	if not db.session.query(User).where(User.id == token.profile_id).first():
		return jsonify({"error": "Current profile is not a user"})

	db.session.query(Profile).where(Profile.id == token.profile_id).update({"name": new_display_name or None})
	db.session.query(User).where(User.id == token.profile_id).update({"biography": new_biography or None})

	date = None
	if new_birthday:
		if datetime.strptime(new_birthday, DATE_FORMAT) < datetime.now():
			date = datetime.strptime(new_birthday, DATE_FORMAT)
		else:
			return jsonify({"error": "Invalid birthday date"})

	db.session.query(User).where(User.id == token.profile_id).update({"birthday": date})

	if new_gender in ["male", "female", "other"]:
		db.session.query(User).where(User.id == token.profile_id).update({"gender": new_gender})
	if new_password:
		db.session.query(Profile).where(Profile.id == token.profile_id).update({"password": hash_secret(new_password)})

	# Update interests
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

	if pfp:
		if len(pfp.read()) > MAX_FILE_SIZE:
			return jsonify({"error": "File too large"})
		pfp.seek(0)
		filename = save_file(pfp, img_only=True)
		try:
			db.session.query(User).where(User.id == token.profile_id).update({"pfp": filename})
		except:
			delete_file(filename)
			raise

	db.session.flush()
	return jsonify({"error": None})



# Get the settings of the current advertiser, indluding "name", "handle", "industry"
@settings.route("/adv", methods=["GET"])
@safeguard
def get_adv_settings():
	token = get_auth_token(request.cookies)
	if not token:
		return jsonify({"error": "Invalid token"})

	adv = db.session.query(Advertiser).where(Advertiser.id == token.profile_id).first()
	if adv:
		return jsonify({"error": None, "adv": adv_settings_schema.dump(adv)})
	return jsonify({"error": "Advertiser not found"})



# Update the settings of the current advertiser
@settings.route("/adv", methods=["PUT"])
@safeguard
def set_adv_settings():
	token = get_auth_token(request.cookies)
	if not token:
		return jsonify({"error": "Invalid token"})

	req = request.get_json()
	new_display_name = req["display_name"]
	new_industry = req["industry"]
	new_password = req["password"]

	if not db.session.query(Advertiser).where(Advertiser.id == token.profile_id).first():
		return jsonify({"error": "Current profile is not an advertiser"})

	db.session.query(Profile).where(Profile.id == token.profile_id).update({"name": new_display_name or None})
	db.session.query(Advertiser).where(Advertiser.id == token.profile_id).update({"industry": new_industry or None})

	if new_password:
		db.session.query(Profile).where(Profile.id == token.profile_id).update({"password": hash_secret(new_password)})

	db.session.flush()
	return jsonify({"error": None})
