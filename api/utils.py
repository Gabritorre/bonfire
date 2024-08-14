import os
import magic
from flask import Response
from config import db, snowflake, app
from models import Interest, PostTag, Profile, AuthToken
from bcrypt import hashpw, gensalt, checkpw
from werkzeug.datastructures import ImmutableMultiDict
from hashlib import sha1
from datetime import datetime, timedelta, timezone

ALLOWED_MIME_TYPES = {
	"image/jpeg": {"jpg", "jpeg"},
	"image/png": {"png"},
	"image/gif": {"gif"},
	"image/svg+xml": {"svg"},
	"video/mp4": {"mp4"},
	"video/x-msvideo": {"avi"},
	"video/quicktime": {"mov"},
	"video/x-matroska": {"mkv"},
}

def hash_secret(pwd: str) -> str:
	return hashpw(pwd.encode("utf-8"), gensalt()).decode("utf-8")

def verify_secret(pwd: str, stored_pwd: str) -> bool:
	return checkpw(pwd.encode("utf-8"), stored_pwd.encode("utf-8"))

def hash_sha1(string: str) -> str:
	return sha1(string.encode("utf-8")).hexdigest()

def set_auth_token(profile: Profile, res: Response) -> None:
	sf = snowflake.generate()

	hashed_sf = hash_sha1(f"{sf}")
	expiration_date = snowflake.creation_date(sf) + timedelta(weeks=1)

	db.session.add(AuthToken(value=hashed_sf, profile_id=profile.id, expiration_date=expiration_date))
	db.session.commit()

	res.set_cookie("auth_token", str(sf), expires=expiration_date)

def get_auth_token(cookies: ImmutableMultiDict[str, str]) -> AuthToken | None:
	token = "auth_token" in cookies and db.session.query(AuthToken).where(AuthToken.value == hash_sha1(str(cookies.get("auth_token"))), AuthToken.expiration_date > datetime.now(timezone.utc)).first()
	if token:
		return token
	else:
		return None

def update_interests(user_id: int, post_id: int, inc: float, dec: float) -> None:
	post_tags = {tag.tag_id for tag in db.session.query(PostTag).where(PostTag.post_id == post_id).all()}
	interests = {interest.tag_id for interest in db.session.query(Interest).where(Interest.user_id == user_id).all()}

	new_interests = post_tags - interests
	for tag in new_interests:
		db.session.add(Interest(user_id=user_id, tag_id=tag, interest=1.0))

	increasing_interests = post_tags - new_interests
	db.session.query(Interest).where(Interest.tag_id.in_(increasing_interests)).update({Interest.interest: Interest.interest + inc})

	decreasing_interests = interests - increasing_interests
	db.session.query(Interest).where(Interest.tag_id.in_(decreasing_interests)).update({Interest.interest: Interest.interest - dec})


def save_file(file) -> str:

	mime = magic.Magic(mime=True)
	mime_type = mime.from_buffer(file.read(2048))
	file.seek(0)
	if mime_type in ALLOWED_MIME_TYPES:
		extension = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else ''
		if extension in ALLOWED_MIME_TYPES[mime_type]:
			sf = snowflake.generate()
			hashed_sf = hash_sha1(f"{sf}")
			new_filename = f"{hashed_sf}.{extension}"
			file.save(os.path.join(app.config["UPLOAD_FOLDER"], new_filename))
			return new_filename
	raise ValueError("Invalid file extension")

def delete_file(filename) -> None:
	file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
	if os.path.exists(file_path):
		os.remove(file_path)
