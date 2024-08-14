from flask import Blueprint, jsonify, request
from config import db, safeguard
from models import DATE_FORMAT, AdCampaign, Advertiser, Ad
from schemas import ads_schema, ad_schema
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



@adv.route("/campaign", methods=["DELETE"])
@safeguard
def delete_campaign():
	token = get_auth_token(request.cookies)
	if not token:
		return jsonify({"error": "Invalid token"})

	req = request.get_json()
	campaign_id = req["id"]
	adv = db.session.query(Advertiser).where(Advertiser.id == token.profile_id).first()
	if not adv:
		return jsonify({"error": "Not an advertiser profile"})
	campaign = db.session.query(AdCampaign).where(AdCampaign.id == campaign_id, AdCampaign.advertiser_id == adv.id).first()
	if not campaign:
		return jsonify({"error": "Campaign doesn't belong to this advertiser or doesn't exist"})
	db.session.delete(campaign)
	db.session.commit()
	return jsonify({"error": None})



@adv.route("/ads", methods=["POST"])
@safeguard
def get_ads():
	token = get_auth_token(request.cookies)
	if not token:
		return jsonify({"error": "Invalid token"})

	req = request.get_json()
	campaign_id = req["campaign_id"]
	adv = db.session.query(Advertiser).where(Advertiser.id == token.profile_id).first()
	if not adv:
		return jsonify({"error": "Not an advertiser profile"})
	campaign = db.session.query(AdCampaign).where(AdCampaign.advertiser_id == adv.id, AdCampaign.id == campaign_id).first()
	if not campaign:
		return jsonify({"error": "Campaign doesn't belong to this advertiser or doesn't exist"})
	ads = db.session.query(Ad).where(Ad.ad_campaign_id == campaign_id).all()
	return jsonify({"error": None, "ads": ads_schema.dump(ads)})



@adv.route("/ad", methods=["POST"])
@safeguard
def get_ad():
	token = get_auth_token(request.cookies)
	if not token:
		return jsonify({"error": "Invalid token"})

	req = request.get_json()
	ad_id = req["id"]
	adv = db.session.query(Advertiser).where(Advertiser.id == token.profile_id).first()
	if not adv:
		return jsonify({"error": "Not an advertiser profile"})

	ad = db.session.query(Ad).where(Ad.id == ad_id).first()
	if not ad:
		return jsonify({"error": "Ad doesn't exist"})
	campaign = db.session.query(AdCampaign).where(AdCampaign.id == ad.ad_campaign_id).first()
	if not campaign or campaign.advertiser_id != adv.id:
		return jsonify({"error": "Ad doesn't belong to this advertiser"})

	return jsonify({"error": None, "ad": ad_schema.dump(ad)})


@adv.route("/ad", methods=["DELETE"])
@safeguard
def delete_ad():
	token = get_auth_token(request.cookies)
	if not token:
		return jsonify({"error": "Invalid token"})

	req = request.get_json()
	ad_id = req["id"]
	adv = db.session.query(Advertiser).where(Advertiser.id == token.profile_id).first()
	if not adv:
		return jsonify({"error": "Not an advertiser profile"})
	ad = db.session.query(Ad).where(Ad.id == ad_id).first()
	if not ad:
		return jsonify({"error": "Ad doesn't exist"})
	campaign = db.session.query(AdCampaign).where(AdCampaign.id == ad.ad_campaign_id).first()
	if not campaign or campaign.advertiser_id != adv.id:
		return jsonify({"error": "Ad doesn't belong to this advertiser"})
	db.session.delete(ad)
	db.session.commit()
	return jsonify({"error": None})
