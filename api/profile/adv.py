from flask import Blueprint, json, jsonify, request
from config import db, safeguard
from models import DATE_FORMAT, AdCampaign, Advertiser, Ad, CampaignTag, DailyStat
from schemas import ads_schema, ad_schema, campaigns_schema, ad_stats_schema
from datetime import datetime, timezone
from api.utils import get_auth_token, save_file, delete_file

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
		if start > datetime.now(timezone.utc) and end > start:
			ad_campaign = AdCampaign(advertiser_id=adv.id, name=name, start_date=start, end_date=end)
			db.session.add(ad_campaign)
			db.session.flush()
			for tag in tags:
				db.session.add(CampaignTag(campaign_id=ad_campaign.id, tag_id=tag))
			db.session.commit()
			return jsonify({"error": None})
		else:
			return jsonify({"error": "End date is previous to start date"})
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
	db.session.commit()
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
@adv.route("/budget", methods=["POST"])
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
	db.session.commit()
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



# Get a specific ad, recognized by its "id", owned by the current advertiser
# Returns the ad's "id", "campaign_id", "name", "media", "link", "probability", "date", "daily_stats"
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
	campaign = db.session.query(AdCampaign).where(AdCampaign.id == ad.campaign_id).first()
	if not campaign or campaign.advertiser_id != adv.id:
		return jsonify({"error": "Ad doesn't belong to this advertiser"})

	return jsonify({"error": None, "ad": ad_schema.dump(ad)})



# Create a new ad for a campaign, recognized by its "id", owned by the current advertiser
# The probability of an ad appearing on a certain campaign is bounded to [0, 1], this is enforced by a database trigger
@adv.route("/ad", methods=["PUT"])
@safeguard
def create_ad():
	token = get_auth_token(request.cookies)
	if not token:
		return jsonify({"error": "Invalid token"})

	req = json.loads(request.form["json"])
	campaign_id = req["id"]
	name = req["name"]
	link = req["link"]
	prob = req["probability"]
	media = request.files["media"]

	filename = None
	if media:
		filename = save_file(media)

	try:
		ad = Ad(campaign_id=campaign_id, name=name, media=filename, link=link, probability=prob)
		db.session.add(ad)
		db.session.commit()
	except:
		if filename:
			delete_file(filename)
		raise

	return jsonify({"error": None})



# Delete an ad, recognized by its "id", owned by the current advertiser
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
	campaign = db.session.query(AdCampaign).where(AdCampaign.id == ad.campaign_id).first()
	if not campaign or campaign.advertiser_id != adv.id:
		return jsonify({"error": "Ad doesn't belong to this advertiser"})
	db.session.delete(ad)
	if ad.media:
		delete_file(ad.media)
	db.session.commit()
	return jsonify({"error": None})



@adv.route("/ad_stats", methods=["POST"])
@safeguard
def get_stats():
	token = get_auth_token(request.cookies)
	if not token:
		return jsonify({"error": "Invalid token"})

	req = request.get_json()
	ad_id = req["id"]
	campaign = db.session.query(AdCampaign).join(Ad, AdCampaign.id == Ad.campaign_id).where(AdCampaign.advertiser_id == token.profile_id, Ad.id == ad_id).first()
	if not campaign:
		return jsonify({"error": "Ad doesn't belong to this advertiser or doesn't exist"})
	stats = db.session.query(DailyStat).join(Ad, DailyStat.ad_id == Ad.id).where(DailyStat.ad_id == ad_id).all()
	return jsonify({"error": None, "stats": ad_stats_schema.dump(stats)})
