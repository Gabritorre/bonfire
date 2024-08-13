from config import ma, db
from models import *
from marshmallow import fields

class ProfileSchema(ma.SQLAlchemyAutoSchema):
	class Meta:
		model = Profile

#todo: join this schema with UserSettingsSchema (?) / create a father class with the common fields?
class UserSchema(ma.SQLAlchemyAutoSchema):
	class Meta:
		model = User
		fields = ("handle", "display_name", "gender", "pfp", "banner", "biography", "birthday", "follower", "following", "interests")

	handle = fields.String(attribute="profile.handle", data_key="handle")
	display_name = fields.String(attribute="profile.name", data_key="display_name")
	follower = fields.Method("get_follower_count_field")
	following = fields.Method("get_following_count_field")
	interests = fields.Method("get_interests_list")

	def get_follower_count_field(self, user_instance):
		return db.session.query(Following).where(Following.followed == user_instance.id).count()

	def get_following_count_field(self, user_instance):
		return db.session.query(Following).where(Following.follower == user_instance.id).count()

	def get_interests_list(self, user_instance):
		interests_list = (db.session.query(Tag.id, Tag.tag)
						.join(Interest)
						.where(Interest.user_id == user_instance.id)
						.all())
		return [{"id": tag_id, "tag": tag_name} for tag_id, tag_name in interests_list]

class UserSettingsSchema(ma.SQLAlchemyAutoSchema):
	class Meta:
		model = User
		fields = ("display_name", "handle", "pfp", "gender", "biography", "birthday", "interests")

	interests = fields.Method("get_interests_list")
	handle = fields.String(attribute="profile.handle", data_key="handle")
	display_name = fields.String(attribute="profile.name", data_key="display_name")

	def get_interests_list(self, user_instance):
		interests_list = (db.session.query(Tag.id, Tag.tag)
						.join(Interest)
						.where(Interest.user_id == user_instance.id)
						.all())
		return [{"id": tag_id, "tag": tag_name} for tag_id, tag_name in interests_list]

class UserIdUsernameSchema(ma.SQLAlchemySchema):
	class Meta:
		model = User
		fields = ("id", "pfp", "handle", "display_name")

	handle = fields.String(attribute="profile.handle", data_key="handle")
	display_name = fields.String(attribute="profile.name", data_key="display_name")

class TagSchema(ma.SQLAlchemyAutoSchema):
	class Meta:
		model = Tag

class PostSchema(ma.SQLAlchemyAutoSchema):
	class Meta:
		model = Post
		fields = ("id", "user_id", "user_display_name", "user_pfp", "body", "media", "date", "likes", "comments", "user_like")

	user_display_name = fields.String(attribute="user.profile.name", data_key="display_name")
	user_pfp = fields.String(attribute="user.pfp", data_key="user_pfp")
	likes = fields.Method("get_likes_count_field")
	comments = fields.Method("get_comments_count_field")
	user_like = fields.Boolean()

	def get_likes_count_field(self, post_instance):
		return db.session.query(Like).where(Like.post_id == post_instance.id, Like.liked == True).count()

	def get_comments_count_field(self, post_instance):
		return db.session.query(Comment).where(Comment.post_id == post_instance.id, Comment.body.isnot(None)).count()


class AdsSchema(ma.SQLAlchemyAutoSchema):
	class Meta:
		model = Ad
		fields = ("id", "name", "media", "date")

class AdSchema(ma.SQLAlchemyAutoSchema):
	class Meta:
		model = Ad
		fields = ("id", "ad_campaign_id", "name", "media", "link", "probability", "date", "daily_stats")

	daily_stats = fields.Method("get_daily_stats_list")

	def get_daily_stats_list(self, ad_instance):
		daily_stats_list = db.session.query(DailyStat).where(DailyStat.ad_id == ad_instance.id).all()
		return [{"date": ds.date.strftime(DATE_FORMAT), "impressions": ds.impressions, "readings": ds.readings, "clicks": ds.clicks} for ds in daily_stats_list]


profile_schema = ProfileSchema()
user_schema = UserSchema()
users_schema = UserSchema(many=True)
id_username_schema = UserIdUsernameSchema(many=True)
tags_schema = TagSchema(many=True)
user_settings_schema = UserSettingsSchema()
posts_schema = PostSchema(many = True)
ads_schema = AdsSchema(many = True)
ad_schema = AdSchema()
