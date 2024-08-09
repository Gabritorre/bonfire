from flask import Blueprint, jsonify, request
from config import db, safeguard
from models import DATE_FORMAT, AdCampaign, Advertiser, AuthToken
from datetime import datetime, timezone
from api.utils import hash_sha1

adv = Blueprint("adv", __name__, url_prefix="/adv")

@adv.route("/create_campaign", methods=["POST"])
@safeguard
def create_campaign():
	if ("auth_token" in request.cookies):
		token = db.session.query(AuthToken).where(AuthToken.value == hash_sha1(str(request.cookies.get("auth_token"))), AuthToken.expiration_date > datetime.now(timezone.utc)).first()
		if token:
			adv = db.session.query(Advertiser).where(Advertiser.id == token.profile_id).first()
			if adv:
				req = request.get_json()
				name = req.get("name")
				budget = req.get("budget")
				start = req.get("start")	# TODO: Check that date parameters are valid, otherwise return error
				end = req.get("end")
				if name and budget and start and end:
					if datetime.strptime(start, DATE_FORMAT) > datetime.now() and end > start:
						db.session.add(AdCampaign(advertiser_id=adv.id, name=name, budget=budget, start=start, end=end))
						db.session.commit()
						return jsonify({"error": None})
				return jsonify({"error": "Invalid Json content"})
	return jsonify({"error": "Invalid token"})
