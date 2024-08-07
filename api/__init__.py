from flask import Blueprint
from .profile import profile
from .user import user
from .settings import settings
from .feed import feed
from .post import post
from .adv import adv

api = Blueprint("api", __name__, url_prefix="/api")
api.register_blueprint(profile)
api.register_blueprint(user)
api.register_blueprint(settings)
api.register_blueprint(feed)
api.register_blueprint(post)
api.register_blueprint(adv)
