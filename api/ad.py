from flask import Blueprint, json, jsonify, request
from config import db, safeguard
from models import AdCampaign, Advertiser, Ad, DailyStat
from schemas import ad_schema, ad_stats_schema
from api.utils import get_auth_token, save_file, delete_file, update_daily_stats

ad = Blueprint("ad", __name__, url_prefix="/ad")

# Get a specific ad, recognized by its "id", owned by the current advertiser
# Returns the ad's "id", "campaign_id", "name", "media", "link", "probability", "date", "daily_stats"
@ad.route("/", methods=["POST"])
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
@ad.route("/", methods=["PUT"])
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

	adv = db.session.query(Advertiser).where(Advertiser.id == token.profile_id).first()
	if not adv:
		return jsonify({"error": "Not an advertiser profile"})
	
	campaign = db.session.query(AdCampaign).where(AdCampaign.id == campaign_id, AdCampaign.advertiser_id == adv.id).first()
	if not campaign:
		return jsonify({"error": "Campaign doesn't belong to this advertiser or doesn't exist"})

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

	return jsonify({"error": None, "ad": ad_schema.dump(ad)})



# Delete an ad, recognized by its "id", owned by the current advertiser
@ad.route("/", methods=["DELETE"])
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



# Get the daily stats of an ad, recognized by its "id", owned by the current advertiser
@ad.route("/stats", methods=["POST"])
@safeguard
def get_stats():
	token = get_auth_token(request.cookies)
	if not token:
		return jsonify({"error": "Invalid token"})

	req = request.get_json()
	ad_id = req["id"]

	adv = db.session.query(Advertiser).where(Advertiser.id == token.profile_id).first()
	if not adv:
		return jsonify({"error": "Not an advertiser profile"})

	campaign = db.session.query(AdCampaign).join(Ad, AdCampaign.id == Ad.campaign_id).where(AdCampaign.advertiser_id == token.profile_id, Ad.id == ad_id).first()
	if not campaign:
		return jsonify({"error": "Ad doesn't belong to this advertiser or doesn't exist"})
	stats = db.session.query(DailyStat).join(Ad, DailyStat.ad_id == Ad.id).where(DailyStat.ad_id == ad_id).all()
	return jsonify({"error": None, "stats": ad_stats_schema.dump(stats)})



# Update the daily stats of an ad, recognized by its "id", owned by the current advertiser
@ad.route("/stats", methods=["PUT"])
@safeguard
def update_stats():
	token = get_auth_token(request.cookies)
	if not token:
		return jsonify({"error": "Invalid token"})
	
	req = request.get_json()
	ad_id = req["id"]
	click = req["clicked"]
	read = req["read"]

	adv = db.session.query(Advertiser).where(Advertiser.id == token.profile_id).first()
	if not adv:
		return jsonify({"error": "Not an advertiser profile"})

	campaign = db.session.query(AdCampaign).join(Ad, AdCampaign.id == Ad.campaign_id).where(AdCampaign.advertiser_id == token.profile_id, Ad.id == ad_id).first()
	if not campaign:
		return jsonify({"error": "Ad doesn't belong to this advertiser or doesn't exist"})
	if click:
		update_daily_stats(ad_id, click=1)
	if read:
		update_daily_stats(ad_id, read=1)
	db.session.commit()
	return jsonify({"error": None})
