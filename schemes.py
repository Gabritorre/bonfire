from config import ma
from models import *

class ProfileSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Profile
        include_fk = True

class UserSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = User
        include_fk = True

class UserIdUsernameSchema(ma.SQLAlchemySchema):
    class Meta:
        model = User
    id = ma.auto_field()

profile_schema = ProfileSchema()
user_schema = UserSchema()
users_schema = UserSchema(many=True)
id_username_schema = UserIdUsernameSchema(many=True)
