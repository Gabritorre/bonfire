from config import ma, db
from models import *
from marshmallow import fields

class ProfileSchema(ma.SQLAlchemyAutoSchema):
	class Meta:
		model = Profile

class UserSchema(ma.SQLAlchemyAutoSchema):
	class Meta:
		model = User
		fields = ("profile.handle", "profile.name", "gender", "pfp", "banner", "biography", "follower", "following")

	follower = fields.Method("get_follower_count_field")
	following = fields.Method("get_following_count_field")
	#todo: add interests

	def get_follower_count_field(self, user_instance):
		return db.session.query(Following).filter(Following.followed == user_instance.id).count()

	def get_following_count_field(self, user_instance):
		return db.session.query(Following).filter(Following.follower == user_instance.id).count()

class UserIdUsernameSchema(ma.SQLAlchemySchema):
	class Meta:
		model = User
		fields = ("id", "pfp", "profile.handle")

class tagSchema(ma.SQLAlchemyAutoSchema):
	class Meta:
		model = Tag

profile_schema = ProfileSchema()
user_schema = UserSchema()
users_schema = UserSchema(many=True)
id_username_schema = UserIdUsernameSchema(many=True)
tags_schema = tagSchema(many=True)
