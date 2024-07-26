import os
from api import api
from flask import render_template, send_from_directory
from config import app, engine, db, ma
from models import *

app.register_blueprint(api)

Base.metadata.create_all(bind=engine)

@app.route("/", defaults={"path": "index"})
@app.route("/<path:path>")
def root(path):
	if not os.path.splitext(path)[1]:
		path = path + ".html"

	if path.endswith(".html"):
		if not os.path.isfile(os.path.join(app.template_folder, path)):
			return (render_template("404.html"), 404)
		return render_template(path)
	else:
		if not os.path.isfile(os.path.join(app.static_folder, path)):
			return (render_template("404.html"), 404)
		return send_from_directory(app.static_folder, path)
