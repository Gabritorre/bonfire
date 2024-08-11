from flask import Blueprint, jsonify, request
from config import db, safeguard
from models import DATE_FORMAT, AdCampaign, Advertiser
from datetime import datetime
from api.utils import get_auth_token

adv = Blueprint("adv", __name__, url_prefix="/adv")

@adv.route("/campaign", methods=["PUT"])
@safeguard
def create_campaign():
	token = get_auth_token(request.cookies)
	if not token:
		return jsonify({"error": "Invalid token"})

	req = request.get_json()
	name = req["name"]
	budget = req["budget"]
	start = req["start"]
	end = req["end"]
	adv = db.session.query(Advertiser).where(Advertiser.id == token.profile_id).first()
	if adv:
		start = datetime.strptime(start, DATE_FORMAT)
		end = datetime.strptime(end, DATE_FORMAT)
		if start > datetime.now() and end > start:
			db.session.add(AdCampaign(advertiser_id=adv.id, name=name, budget=budget, start_date=start, end_date=end))
			db.session.commit()
			return jsonify({"error": None})
		else:
			return jsonify({"error": "End date is previous to start date"})
	else:
		return jsonify({"error": "Advertiser not found"})
