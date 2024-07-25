import os
from api.user import user
from flask import Flask, render_template, send_from_directory
from config import engine, db, connection_string
from dotenv import load_dotenv
from models import *

app = Flask(__name__)
app.config["secret_key"] = os.getenv("DB_SECRET_KEY")
app.config["SQLALCHEMY_DATABASE_URI"] = connection_string

app.register_blueprint(user)

# db.init_app(app)

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
