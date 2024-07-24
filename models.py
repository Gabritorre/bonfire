import enum as py_enum
from datetime import datetime
from sqlalchemy import Boolean, Float, Integer, LargeBinary, String, DateTime, ForeignKey, Text, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

# TODO: 各フィールドの最大サイズを指定する

class SexEnum(py_enum.Enum):
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"

class RelationEnum(py_enum.Enum):
    FOLLOWER = 'follower'
    FOLLOWING = 'following'
    # BLOCKED?

class Base(DeclarativeBase):
    pass


class Profile(Base):
    __tablename__ = "profiles"
    id: Mapped[int] = mapped_column(Integer, autoincrement=True, primary_key=True)

    password: Mapped[str] = mapped_column(nullable=False)
    email: Mapped[str] = mapped_column(nullable=True)
    creation_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)


# --- Advertisers ---
class Advertiser(Base):
    __tablename__ = "advertisers"
    id: Mapped[int] = mapped_column(ForeignKey("profiles.id"), primary_key=True)

    company_handle: Mapped[str] = mapped_column(String(30), nullable=False, unique=True)
    name: Mapped[str] = mapped_column(String(20), nullable=False)
    industry: Mapped[str] = mapped_column(String(30), nullable=False)


class AdCampaign(Base):
    __tablename__ = "ad_campaign"
    id: Mapped[int] = mapped_column(Integer, autoincrement=True, primary_key=True)
    advertiser: Mapped[int] = mapped_column(ForeignKey("advertisers.id"))

    name: Mapped[str] = mapped_column(String(30), nullable=False)
    budget: Mapped[float] = mapped_column(Float, nullable=False)
    start: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    end: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class Ad(Base):
    __tablename__ = "ads"
    id: Mapped[int] = mapped_column(Integer, autoincrement=True, primary_key=True)
    ad_campaign: Mapped[int] = mapped_column(ForeignKey("ad_campaign.id"))


    body: Mapped[str] = mapped_column(Text, nullable=True) # aggiungere vincolo (body || media)
    media: Mapped[bytes] = mapped_column(LargeBinary, nullable=True)
    link: Mapped[str] = mapped_column(String(20), nullable=True)
    probability: Mapped[float] = mapped_column(Float, nullable=False)


class DailyStat(Base):
    __tablename__ = "daily_stats"
    ad: Mapped[int] = mapped_column(ForeignKey("ads.id"), primary_key=True)
    date: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), primary_key=True)

    impressions: Mapped[int] = mapped_column(Integer)
    readings: Mapped[int] = mapped_column(Integer)
    clicks: Mapped[int] = mapped_column(Integer)


class TargettedTag(Base):
    __tablename__ = "targetted_tags"

    ad: Mapped[int] = mapped_column(ForeignKey("ads.id"), primary_key=True)
    tag: Mapped[int] = mapped_column(Integer, ForeignKey("tags.id"), primary_key=True)
# ------


class Tag(Base):
    __tablename__ = "tags"
    id: Mapped[int] = mapped_column(Integer, autoincrement=True, primary_key=True)

    tag: Mapped[str] = mapped_column(String(10), unique=True, nullable=False)


# --- Users ---
class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(ForeignKey("profiles.id"), primary_key=True)

    user_handle: Mapped[str] = mapped_column(String(30), nullable=False, unique=True)
    name: Mapped[str] = mapped_column(String(20), nullable=False)
    surname: Mapped[str] = mapped_column(String(20), nullable=False)
    #sex: Mapped[SexEnum] = mapped_column(Enum, nullable=False) # TODO
    pfp: Mapped[bytes] = mapped_column(LargeBinary, nullable=True)
    banner: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)
    biography: Mapped[str] = mapped_column(Text, nullable=True)
    followers: Mapped[int] = mapped_column(Integer, nullable=False)
    following: Mapped[int] = mapped_column(Integer, nullable=False)


class Interest(Base):
    __tablename__ = "interests"
    user: Mapped[int] = mapped_column(ForeignKey("users.id"), primary_key=True)
    tag: Mapped[int] = mapped_column(ForeignKey("tags.id"), primary_key=True)

    interest: Mapped[float] = mapped_column(Float, nullable=False)


class Post(Base):
    __tablename__ = "posts"
    id: Mapped[int] = mapped_column(Integer, autoincrement=True, primary_key=True)
    user: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))

    body: Mapped[str] = mapped_column(Text, nullable=True) # aggiungere vincolo (body || media)
    media: Mapped[bytes] = mapped_column(LargeBinary, nullable=True)
    date: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    likes: Mapped[int] = mapped_column(Integer, nullable=False)
    dislikes: Mapped[int] = mapped_column(Integer, nullable=False)


class PostTag(Base):
    __tablename__ = "post_tags"
    post: Mapped[int] = mapped_column(Integer, ForeignKey("posts.id"), primary_key=True)
    tag: Mapped[int] = mapped_column(ForeignKey("tags.id"), primary_key=True)


class UserInteraction(Base):
    __tablename__ = "user_interactions"
    user: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), primary_key=True)
    post: Mapped[int] = mapped_column(Integer, ForeignKey("posts.id"), primary_key=True)

    like: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    dislike: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    comment: Mapped[str] = mapped_column(Text, nullable=True)

class RelationShip(Base):
    __tablename__ = "relationships"
    user1: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), primary_key=True)
    user2: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), primary_key=True)
    #relation: Mapped[RelationEnum] = mapped_column(Enum, nullable=False, name="relation") # TODO
