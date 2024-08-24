import os
import random
import magic
from flask import Response
from sqlalchemy.sql.expression import func
from config import db, snowflake, app
from models import Ad, AdCampaign, CampaignTag, DailyStat, Interest, PostTag, Profile, AuthToken, Like, Comment
from bcrypt import hashpw, gensalt, checkpw
from werkzeug.datastructures import ImmutableMultiDict
from hashlib import sha1
from datetime import datetime, timedelta, timezone

ALLOWED_MIME_TYPES = {
	"image/jpeg": {"jpg", "jpeg"},
	"image/png": {"png"},
	"image/gif": {"gif"},
	"image/webp": {"webp"},
	"video/mp4": {"mp4"},
	"video/ogg": {"ogg", "ogv"},
	"video/webm": {"webm"},
}

MAX_FILE_SIZE = 16 * 1024 * 1024 # 16 MB

IMPRESSION_FEE = 1
READ_FEE = 2
CLICK_FEE = 3

def hash_secret(pwd: str) -> str:
	return hashpw(pwd.encode("utf-8"), gensalt()).decode("utf-8")

def verify_secret(pwd: str, stored_pwd: str) -> bool:
	return checkpw(pwd.encode("utf-8"), stored_pwd.encode("utf-8"))

def hash_sha1(string: str) -> str:
	return sha1(string.encode("utf-8")).hexdigest()

# Set a new auth token for the user in the response's cookies
def set_auth_token(profile: Profile, res: Response) -> None:
	sf = snowflake.generate()

	hashed_sf = hash_sha1(str(sf))
	expiration_date = snowflake.creation_date(sf) + timedelta(weeks=1)

	db.session.add(AuthToken(value=hashed_sf, profile_id=profile.id, expiration_date=expiration_date))
	db.session.flush()

	# TODO: set secure=True if the connection uses https
	res.set_cookie("auth_token", str(sf), expires=expiration_date, httponly=True, samesite="strict")

# Get the token object from the cookies of the request
def get_auth_token(cookies: ImmutableMultiDict[str, str]) -> AuthToken | None:
	token = "auth_token" in cookies and db.session.query(AuthToken).where(AuthToken.value == hash_sha1(str(cookies.get("auth_token"))), AuthToken.expiration_date > datetime.now(timezone.utc)).first()
	if token:
		return token
	else:
		return None

# Update the interests of a user based on a post's tags and the current user interests
# The interests are always >= 0, this is enforced by a database trigger
def update_interests(user_id: int, post_id: int, inc: float=0.0, dec: float=0.0) -> None:
	post_tags = {tag.tag_id for tag in db.session.query(PostTag).where(PostTag.post_id == post_id).all()}

	if len(post_tags) > 0:
		interests = {interest.tag_id for interest in db.session.query(Interest).where(Interest.user_id == user_id).all()}
		new_interests = post_tags - interests
		for tag in new_interests:
			db.session.add(Interest(user_id=user_id, tag_id=tag, interest=inc))

		increasing_interests = post_tags - new_interests
		db.session.query(Interest).where(Interest.tag_id.in_(increasing_interests), Interest.user_id == user_id).update({Interest.interest: Interest.interest + inc})

		decreasing_interests = interests - increasing_interests
		db.session.query(Interest).where(Interest.tag_id.in_(decreasing_interests), Interest.user_id == user_id).update({Interest.interest: Interest.interest + dec})

# Save a file in the server filesystem, before saving the file, the mime type and extensiona are validated and the filename is hashed
def save_file(file, img_only = False) -> str:
	mime = magic.Magic(mime=True)
	mime_type = mime.from_buffer(file.read(2048))
	file.seek(0)

	if (img_only and not mime_type.startswith("image/")) or mime_type not in ALLOWED_MIME_TYPES:
		raise ValueError("Invalid file type")

	extension = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else ''
	if extension in ALLOWED_MIME_TYPES[mime_type]:
		sf = snowflake.generate()
		new_filename = f"{sf}.{extension}"
		new_path = os.path.join(app.config["UPLOAD_FOLDER"], new_filename)
		file.save(new_path)
		return os.path.join("/", new_path)
	raise ValueError("Invalid file extension")

# Delete a file from the server filesystem
def delete_file(filename) -> None:
	file_path = os.path.join(app.root_path, filename.strip("/"))
	if os.path.exists(file_path):
		os.remove(file_path)

# Update the daily stats of an advertisement
def update_daily_stats(ad_id: int | None, impression: int=0, read: int=0, click: int=0) -> None:
	if ad_id:
		today = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
		d_stat = db.session.query(DailyStat).where(DailyStat.ad_id == ad_id, DailyStat.date == today).first()
		if d_stat:
			d_stat.impressions += impression
			d_stat.readings += read
			d_stat.clicks += click
		else:
			db.session.add(DailyStat(ad_id=ad_id, date=today, impressions=impression, readings=read, clicks=click))


# Select a recommend ad to a user based on their interests and the campaign budget
def recommend_ad(user_id: int | None, epsilon: float=0.8) -> Ad | None:
	fees = IMPRESSION_FEE + READ_FEE + CLICK_FEE
	if user_id:
		hi_interest = db.session.query(Interest).where(Interest.user_id == user_id).order_by(Interest.interest.desc()).first() # highest interest
		if hi_interest:
			interested_campaign = (db.session.query(AdCampaign) # campaign with highest budget that matches hi_interest
							.join(CampaignTag, AdCampaign.id == CampaignTag.campaign_id)
							.where(CampaignTag.tag_id == hi_interest.tag_id,
								AdCampaign.start_date < datetime.now(timezone.utc),
								AdCampaign.end_date > datetime.now(timezone.utc),
								AdCampaign.budget >= fees,
								AdCampaign.advertiser_id != user_id)
							.order_by(AdCampaign.budget.desc())
							.first())

			if interested_campaign and db.session.query(Ad).where(Ad.campaign_id == interested_campaign.id).first(): # the interested campaign has at least an ad
				if random.random() < epsilon: # choose an ad inside interested_campaign with epsilon probability or explore other ads
					ads = db.session.query(Ad).where(Ad.campaign_id == interested_campaign.id).all()
					if len(ads) > 0:
						probs = [ad.probability for ad in ads]
						recommended_ad = random.choices(ads, weights=probs, k=1)[0]
						interested_campaign.budget -= IMPRESSION_FEE
						update_daily_stats(recommended_ad.id, impression=1)
						return recommended_ad
					else:
						return None

	res = (db.session.query(Ad, AdCampaign)
		.join(AdCampaign, Ad.campaign_id == AdCampaign.id)
		.where(AdCampaign.start_date < datetime.now(timezone.utc),
			AdCampaign.end_date > datetime.now(timezone.utc),
			AdCampaign.budget >= fees,
			AdCampaign.advertiser_id != user_id)
		.order_by(func.random())
		.first()) # select a random ad
	if res:
		recommended_ad, interested_campaign = res
		interested_campaign.budget -= IMPRESSION_FEE
		update_daily_stats(recommended_ad.id, impression=1)
		return recommended_ad

# for each post check if the current user liked it or not
def set_user_like(posts, post_data, profile_id):
	post_ids = [post.id for post in posts]
	user_likes = (db.session.query(Like.post_id)
				.where(Like.user_id == profile_id, Like.post_id.in_(post_ids))
				.all())
	liked_post_ids = {like.post_id for like in user_likes}
	for count, post in enumerate(posts):
		post_data[count]["user_like"] = post.id in liked_post_ids

# for each post set the number of likes
def set_likes_count(posts, posts_data):
	post_ids = [post.id for post in posts]
	like_counts = (db.session.query(Like.post_id, func.count().label("like_count"))
				.where(Like.post_id.in_(post_ids))
				.group_by(Like.post_id)
				.all())
	like_count_dict = {post_id: like_count for post_id, like_count in like_counts}
	for post_data in posts_data:
		post_data["likes"] = like_count_dict.get(post_data["id"], 0)

# for each post set the number of comments
def set_comments_count(posts, posts_data):
	post_ids = [post.id for post in posts]
	comment_counts = (db.session.query(Comment.post_id, func.count().label("comment_count"))
					.where(Comment.post_id.in_(post_ids), Comment.body.isnot(None))
					.group_by(Comment.post_id)
					.all())
	comment_count_dict = {post_id: comment_count for post_id, comment_count in comment_counts}
	for post_data in posts_data:
		post_data["comments"] = comment_count_dict.get(post_data["id"], 0)
