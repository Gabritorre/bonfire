from config import ma, db
from models import *
from marshmallow import fields

class ProfileSchema(ma.SQLAlchemyAutoSchema):
	class Meta:
		model = Profile


class UserSchema(ma.SQLAlchemyAutoSchema):
	class Meta:
		model = User
		fields = ("handle", "name", "creation_date", "gender", "pfp", "biography", "birthday", "follower", "following", "interests", "followed")

	handle = fields.String(attribute="profile.handle", data_key="handle")
	name = fields.String(attribute="profile.name", data_key="name")
	creation_date = fields.DateTime(format=DATE_TIME_FORMAT, attribute="profile.creation_date", data_key="creation_date")
	follower = fields.Method("get_follower_count_field")
	following = fields.Method("get_following_count_field")
	interests = fields.Method("get_interests_list")
	followed = fields.Boolean()

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
		fields = ("name", "handle", "pfp", "gender", "biography", "birthday", "interests")

	interests = fields.Method("get_interests_list")
	handle = fields.String(attribute="profile.handle", data_key="handle")
	name = fields.String(attribute="profile.name", data_key="name")

	def get_interests_list(self, user_instance):
		interests_list = (db.session.query(Tag.id, Tag.tag)
						.join(Interest)
						.where(Interest.user_id == user_instance.id)
						.all())
		return [{"id": tag_id, "tag": tag_name} for tag_id, tag_name in interests_list]


class UserIdUsernameSchema(ma.SQLAlchemySchema):
	class Meta:
		model = User
		fields = ("id", "pfp", "handle", "name")

	handle = fields.String(attribute="profile.handle", data_key="handle")
	name = fields.String(attribute="profile.name", data_key="name")


class TagSchema(ma.SQLAlchemyAutoSchema):
	class Meta:
		model = Tag


class PostSchema(ma.SQLAlchemyAutoSchema):
	class Meta:
		model = Post
		fields = ("id", "user_id", "user_handle", "user_name", "user_pfp", "body", "media", "date", "likes", "comments", "user_like")

	user_handle = fields.String(attribute="user.profile.handle", data_key="user_handle")
	user_name = fields.String(attribute="user.profile.name", data_key="user_name")
	user_pfp = fields.String(attribute="user.pfp", data_key="user_pfp")
	likes = fields.Integer()
	comments = fields.Integer()
	user_like = fields.Boolean()
	date = fields.DateTime(format=DATE_TIME_FORMAT)


class AdSchema(ma.SQLAlchemyAutoSchema):
	class Meta:
		model = Ad
		fields = ("id", "campaign_id", "name", "media", "link", "probability", "date", "daily_stats")

	daily_stats = fields.Method("get_daily_stats_list")
	date = fields.DateTime(format=DATE_TIME_FORMAT)

	def get_daily_stats_list(self, ad_instance):
		daily_stats_list = db.session.query(DailyStat).where(DailyStat.ad_id == ad_instance.id).all()
		return [{"date": ds.date.strftime(DATE_FORMAT), "impressions": ds.impressions, "readings": ds.readings, "clicks": ds.clicks} for ds in daily_stats_list]


class SimpleAdSchema(ma.SQLAlchemyAutoSchema):
	class Meta:
		model = Ad
		fields = ("id", "campaign_id", "name", "media", "link", "date")

	date = fields.DateTime(format=DATE_TIME_FORMAT)


class CommentSchema(ma.SQLAlchemyAutoSchema):
	class Meta:
		model = Comment
		fields = ("id", "user_id", "user_handle", "user_name", "user_pfp", "body", "date")

	date = fields.DateTime(format=DATE_TIME_FORMAT)
	user_handle = fields.String(attribute="user.profile.handle", data_key="user_handle")
	user_name = fields.String(attribute="user.profile.name", data_key="user_name")
	user_pfp = fields.String(attribute="user.pfp", data_key="user_pfp")


class AdvSettingsSchema(ma.SQLAlchemyAutoSchema):
	class Meta:
		model = Advertiser
		fields = ("name", "handle", "industry")

	handle = fields.String(attribute="profile.handle", data_key="handle")
	name = fields.String(attribute="profile.name", data_key="name")


class AdCampaignsSchema(ma.SQLAlchemyAutoSchema):
	class Meta:
		model = AdCampaign
		fields = ("id", "name", "budget", "start_date", "end_date")

	start_date = fields.DateTime(format=DATE_FORMAT)
	end_date = fields.DateTime(format=DATE_FORMAT)
	budget = fields.Float()


class AdStatsSchema(ma.SQLAlchemyAutoSchema):
	class Meta:
		model = DailyStat
		fields = ("id", "impressions", "readings", "clicks", "date")

	date = fields.DateTime(format=DATE_FORMAT)



profile_schema = ProfileSchema()
user_schema = UserSchema()
users_schema = UserSchema(many=True)
id_username_schema = UserIdUsernameSchema(many=True)
tags_schema = TagSchema(many=True)
user_settings_schema = UserSettingsSchema()
post_schema = PostSchema()
posts_schema = PostSchema(many=True)
ad_schema = AdSchema()
feed_ad_schema = SimpleAdSchema()
ads_schema = SimpleAdSchema(many=True)
comments_schema = CommentSchema(many=True)
adv_settings_schema = AdvSettingsSchema()
campaigns_schema = AdCampaignsSchema(many=True)
campaign_schema = AdCampaignsSchema()
ad_stats_schema = AdStatsSchema(many=True)
