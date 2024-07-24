import os
from api import api
from flask import Flask, render_template, send_from_directory
from config import engine
from dotenv import load_dotenv

app = Flask(__name__)
app.config["secret_key"] = os.getenv("DB_SECRET_KEY")
app.register_blueprint(api)

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
