import os
from api import api
from flask import render_template, send_from_directory
from config import app
from models import *

app.register_blueprint(api)


@app.route("/", defaults={"path": "index"})
@app.route("/<path:path>")
def root(path):
	if not os.path.splitext(path)[1]:
		path = path + ".html"

	if path.endswith(".html"):
		if not os.path.isfile(os.path.join(app.root_path, app.template_folder, path)):
			return (render_template("404.html"), 404)
		return render_template(path)
	else:
		if not os.path.isfile(os.path.join(app.root_path, app.static_folder, path)):
			return (render_template("404.html"), 404)
		return send_from_directory(app.static_folder, path)

@app.route("/media/<path:path>")
def media(path):
	if not os.path.isfile(os.path.join(app.root_path, app.config["UPLOAD_FOLDER"], path)):
		return (render_template("404.html"), 404)
	return send_from_directory(app.config["UPLOAD_FOLDER"], path)
