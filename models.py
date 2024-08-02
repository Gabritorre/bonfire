import enum as py_enum
from datetime import datetime
from sqlalchemy import Boolean, Enum, Float, Integer, String, DateTime, ForeignKey, Text, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, backref

NAME_LENGTH = 20
TOKEN_LENGTH = 40
SECRET_LENGTH = 60
DATE_FORMAT = "%Y-%m-%d"	#YYYY-MM-DD

# CREATE TYPE GenderEnum AS ENUM ('male', 'female', 'other')
class GenderEnum(str, py_enum.Enum):
	MALE = "male"
	FEMALE = "female"
	OTHER = "other"

class Base(DeclarativeBase):
	pass


class Profile(Base):
	__tablename__ = "profiles"
	id: Mapped[int] = mapped_column(Integer, autoincrement=True, primary_key=True)

	name: Mapped[str] = mapped_column(String(NAME_LENGTH), nullable=True)
	handle: Mapped[str] = mapped_column(String(NAME_LENGTH), nullable=False, unique=True)
	password: Mapped[str] = mapped_column(String(SECRET_LENGTH), nullable=False)
	creation_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)



# --- Advertisers ---
class Advertiser(Base):
	__tablename__ = "advertisers"
	id: Mapped[int] = mapped_column(ForeignKey("profiles.id",  ondelete="cascade"), primary_key=True)

	industry: Mapped[str] = mapped_column(String(NAME_LENGTH), nullable=True)

	profile: Mapped[Profile] = relationship(backref=backref("ad_profile", cascade="all, delete"), passive_deletes=True)



class AdCampaign(Base):
	__tablename__ = "ad_campaigns"
	id: Mapped[int] = mapped_column(Integer, autoincrement=True, primary_key=True)
	advertiser_id: Mapped[int] = mapped_column(ForeignKey("advertisers.id", ondelete="cascade"))

	name: Mapped[str] = mapped_column(String(NAME_LENGTH), nullable=False)
	budget: Mapped[float] = mapped_column(Float, nullable=False)
	start: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
	end: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

	advertiser: Mapped[Advertiser] = relationship(backref=backref("advertisers", cascade="all, delete"), passive_deletes=True)



class Ad(Base):
	__tablename__ = "ads"
	id: Mapped[int] = mapped_column(Integer, autoincrement=True, primary_key=True)
	ad_campaign_id: Mapped[int] = mapped_column(ForeignKey("ad_campaigns.id", ondelete="cascade"))

	media: Mapped[str] = mapped_column(Text, nullable=True)
	link: Mapped[str] = mapped_column(Text, nullable=True)
	probability: Mapped[float] = mapped_column(Float, nullable=False)

	ad_campaign: Mapped[AdCampaign] = relationship(backref=backref("ad_campaigns", cascade="all, delete"), passive_deletes=True)



class DailyStat(Base):
	__tablename__ = "daily_stats"
	ad_id: Mapped[int] = mapped_column(ForeignKey("ads.id", ondelete="cascade"), primary_key=True)
	date: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), primary_key=True)

	impressions: Mapped[int] = mapped_column(Integer)
	readings: Mapped[int] = mapped_column(Integer)
	clicks: Mapped[int] = mapped_column(Integer)

	ad: Mapped[Ad] = relationship(backref=backref("ads_daily", cascade="all, delete"), passive_deletes=True)


class Tag(Base):
	__tablename__ = "tags"
	id: Mapped[int] = mapped_column(Integer, autoincrement=True, primary_key=True)

	tag: Mapped[str] = mapped_column(Text, unique=True, nullable=False)


class TargetedTag(Base):
	__tablename__ = "targeted_tags"
	ad_id: Mapped[int] = mapped_column(ForeignKey("ads.id", ondelete="cascade"), primary_key=True)
	tag_id: Mapped[int] = mapped_column(ForeignKey("tags.id", ondelete="cascade"), primary_key=True)

	ad: Mapped[Ad] = relationship(backref=backref("ads", cascade="all, delete"), passive_deletes=True)
	tag: Mapped[Tag] = relationship(backref=backref("tags_target", cascade="all, delete"), passive_deletes=True)

# ------



# --- Users ---
class User(Base):
	__tablename__ = "users"
	id: Mapped[int] = mapped_column(ForeignKey("profiles.id", ondelete="cascade"), primary_key=True)

	gender: Mapped[GenderEnum] = mapped_column(Enum(GenderEnum), nullable=True)
	pfp: Mapped[str] = mapped_column(Text, nullable=True)
	banner: Mapped[str] = mapped_column(Text, nullable=True)
	biography: Mapped[str] = mapped_column(String(420), nullable=True)
	birthday: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)

	profile: Mapped[Profile] = relationship(backref=backref("user_profile", cascade="all, delete"), passive_deletes=True, lazy='joined', single_parent=True)


class Interest(Base):
	__tablename__ = "interests"
	user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="cascade"), primary_key=True)
	tag_id: Mapped[int] = mapped_column(ForeignKey("tags.id", ondelete="cascade"), primary_key=True)

	interest: Mapped[float] = mapped_column(Float, nullable=False)

	user: Mapped[User] = relationship(backref=backref("users", cascade="all, delete"), passive_deletes=True)
	tag: Mapped[Tag] = relationship(backref=backref("tags", cascade="all, delete"), passive_deletes=True)



class AuthToken(Base):
	__tablename__ = "auth_tokens"
	value: Mapped[str] = mapped_column(String(TOKEN_LENGTH), primary_key=True)
	profile_id: Mapped[int] = mapped_column(ForeignKey("profiles.id", ondelete="cascade"), nullable=True)

	expiration_date: Mapped[datetime] = mapped_column(DateTime(timezone=True))

	profile: Mapped[Profile] = relationship(backref=backref("profile_token", cascade="all, delete"), primaryjoin="AuthToken.profile_id == Profile.id", passive_deletes=True)



class Post(Base):
	__tablename__ = "posts"
	id: Mapped[int] = mapped_column(Integer, autoincrement=True, primary_key=True)
	user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="cascade"))

	body: Mapped[str] = mapped_column(String(420), nullable=True) # aggiungere vincolo (body || media)
	media: Mapped[str] = mapped_column(Text, nullable=True)
	date: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

	user: Mapped[User] = relationship(backref=backref("users_post", cascade="all, delete"), passive_deletes=True)



class PostTag(Base):
	__tablename__ = "post_tags"
	post_id: Mapped[int] = mapped_column(ForeignKey("posts.id", ondelete="cascade"), primary_key=True)
	tag_id: Mapped[int] = mapped_column(ForeignKey("tags.id", ondelete="cascade"), primary_key=True)

	post: Mapped[Post] = relationship(backref=backref("posts", cascade="all, delete"), passive_deletes=True)
	tag: Mapped[Tag] = relationship(backref=backref("tags_post", cascade="all, delete"), passive_deletes=True)



class UserInteraction(Base):
	__tablename__ = "user_interactions"
	user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="cascade"), primary_key=True)
	post_id: Mapped[int] = mapped_column(ForeignKey("posts.id", ondelete="cascade"), primary_key=True)

	liked: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
	comment: Mapped[str] = mapped_column(String(420), nullable=True)

	user: Mapped[User] = relationship(backref=backref("users_interaction", cascade="all, delete"), passive_deletes=True)
	post: Mapped[Post] = relationship(backref=backref("posts_interaction", cascade="all, delete"), passive_deletes=True)



class Following(Base):
	__tablename__ = "followings"
	follower: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="cascade"), primary_key=True)
	followed: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="cascade"), primary_key=True)

	user1: Mapped[User] = relationship(backref=backref("users1", cascade="all, delete"), primaryjoin="Following.follower == User.id", passive_deletes=True)
	user2: Mapped[User] = relationship(backref=backref("users2", cascade="all, delete"), primaryjoin="Following.followed == User.id", passive_deletes=True)
