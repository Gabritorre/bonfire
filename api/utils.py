from flask import Response
from config import db, snowflake
from models import Profile, AuthToken
from bcrypt import hashpw, gensalt, checkpw
from hashlib import sha1
from datetime import timedelta

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
