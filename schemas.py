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
		fields = ("username", "display_name", "gender", "pfp", "banner", "biography", "birthday", "follower", "following", "interests")

	username = fields.String(attribute="profile.handle", data_key="username")
	display_name = fields.String(attribute="profile.name", data_key="display_name")
	follower = fields.Method("get_follower_count_field")
	following = fields.Method("get_following_count_field")
	interests = fields.Method("get_interests_list")

	def get_follower_count_field(self, user_instance):
		return db.session.query(Following).filter(Following.followed == user_instance.id).count()

	def get_following_count_field(self, user_instance):
		return db.session.query(Following).filter(Following.follower == user_instance.id).count()

	def get_interests_list(self, user_instance):
		interests_list = (db.session.query(Tag.id, Tag.tag)
						.join(Interest)
						.filter(Interest.user_id == user_instance.id)
						.all())
		return [{"id": tag_id, "tag": tag_name} for tag_id, tag_name in interests_list]

class UserSettingsSchema(ma.SQLAlchemyAutoSchema):
	class Meta:
		model = User
		fields = ("display_name", "username", "gender", "biography", "birthday", "interests")

	interests = fields.Method("get_interests_list")
	username = fields.String(attribute="profile.handle", data_key="username")
	display_name = fields.String(attribute="profile.name", data_key="display_name")

	def get_interests_list(self, user_instance):
		interests_list = (db.session.query(Tag.id, Tag.tag)
						.join(Interest)
						.filter(Interest.user_id == user_instance.id)
						.all())
		return [{"id": tag_id, "tag": tag_name} for tag_id, tag_name in interests_list]

class UserIdUsernameSchema(ma.SQLAlchemySchema):
	class Meta:
		model = User
		fields = ("id", "pfp", "profile.handle")

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
		return db.session.query(UserInteraction).filter(UserInteraction.post_id == post_instance.id, UserInteraction.liked == True).count()

	def get_comments_count_field(self, post_instance):
		return db.session.query(UserInteraction).filter(UserInteraction.post_id == post_instance.id, UserInteraction.comment.isnot(None)).count()

profile_schema = ProfileSchema()
user_schema = UserSchema()
users_schema = UserSchema(many=True)
id_username_schema = UserIdUsernameSchema(many=True)
tags_schema = TagSchema(many=True)
user_settings_schema = UserSettingsSchema()
posts_schema = PostSchema(many = True)
