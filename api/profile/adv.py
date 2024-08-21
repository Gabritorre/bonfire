from flask import Blueprint, jsonify, request
from config import db, safeguard
from models import DATE_FORMAT, Ad, AdCampaign, Advertiser, CampaignTag
from schemas import campaigns_schema, campaign_schema, ads_schema
from datetime import datetime
from api.utils import get_auth_token

adv = Blueprint("adv", __name__, url_prefix="/adv")

# Create a new campaign for the current advertiser
@adv.route("/campaign", methods=["PUT"])
@safeguard
def create_campaign():
	token = get_auth_token(request.cookies)
	if not token:
		return jsonify({"error": "Invalid token"})

	req = request.get_json()
	name = req["name"]
	start = req["start"]
	end = req["end"]
	tags = req["tags"]
	adv = db.session.query(Advertiser).where(Advertiser.id == token.profile_id).first()
	if adv:
		start = datetime.strptime(start, DATE_FORMAT)
		end = datetime.strptime(end, DATE_FORMAT)
		if start.date() < datetime.now().date():
			return jsonify({"error": "Start date is previous to current date"})
		if end <= start:
			return jsonify({"error": "End date is previous or equal to start date"})
		ad_campaign = AdCampaign(advertiser_id=adv.id, name=name, start_date=start, end_date=end)
		db.session.add(ad_campaign)
		db.session.flush()
		for tag in tags:
			db.session.add(CampaignTag(campaign_id=ad_campaign.id, tag_id=tag))
		db.session.flush()

		return jsonify({"error": None, "campaign": campaign_schema.dump(ad_campaign)})
	else:
		return jsonify({"error": "Advertiser not found"})



# Delete a campaign, recognized by its "id", owned by the current advertiser
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
	db.session.flush()
	return jsonify({"error": None})



# Lists the details of each campaign created by the current advertiser
@adv.route("/campaigns", methods=["POST"])
@safeguard
def get_campaigns():
	token = get_auth_token(request.cookies)
	if not token:
		return jsonify({"error": "Invalid token"})

	adv = db.session.query(Advertiser).where(Advertiser.id == token.profile_id).first()
	if not adv:
		return jsonify({"error": "Not an advertiser profile"})
	campaigns = db.session.query(AdCampaign).where(AdCampaign.advertiser_id == adv.id)
	return jsonify({"error": None, "campaigns": campaigns_schema.dump(campaigns)})



# Adds new funds for the specified campaign
@adv.route("/budget", methods=["PUT"])
@safeguard
def add_budget():
	token = get_auth_token(request.cookies)
	if not token:
		return jsonify({"error": "Invalid token"})

	req = request.get_json()
	campaign_id = req["id"]
	added_funds = req["funds"]
	if added_funds < 0:
		return jsonify({"error": "Funds cannot be negative"})

	adv = db.session.query(Advertiser).where(Advertiser.id == token.profile_id).first()
	if not adv:
		return jsonify({"error": "Not an advertiser profile"})
	db.session.query(AdCampaign).where(AdCampaign.id == campaign_id, AdCampaign.advertiser_id == adv.id).update({AdCampaign.budget: AdCampaign.budget + added_funds})
	db.session.flush()
	return jsonify({"error": None})



# Get all ads of a campaign, recognized by its "id", owned by the current advertiser.
# Returns a list of ads that includes their "id", "campaign_id", "name", "media", "link", "date"
@adv.route("/ads", methods=["POST"])
@safeguard
def get_ads():
	token = get_auth_token(request.cookies)
	if not token:
		return jsonify({"error": "Invalid token"})

	req = request.get_json()
	campaign_id = req["id"]
	adv = db.session.query(Advertiser).where(Advertiser.id == token.profile_id).first()
	if not adv:
		return jsonify({"error": "Not an advertiser profile"})
	campaign = db.session.query(AdCampaign).where(AdCampaign.advertiser_id == adv.id, AdCampaign.id == campaign_id).first()
	if not campaign:
		return jsonify({"error": "Campaign doesn't belong to this advertiser or doesn't exist"})
	ads = db.session.query(Ad).where(Ad.campaign_id == campaign_id).all()
	return jsonify({"error": None, "ads": ads_schema.dump(ads)})
