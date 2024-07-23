from api import api
from flask import Flask, jsonify

app = Flask(__name__)
app.register_blueprint(api)

@app.route("/", defaults={"path": "index.html"})
@app.route("/<path:path>")
def root(path):
	return f"<h1>Static content {path}</h1>"
