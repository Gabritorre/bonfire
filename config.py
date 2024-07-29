import os
from dotenv import load_dotenv
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from sqlalchemy import URL, create_engine

load_dotenv()


connection_string = URL.create(
	str(os.getenv("DB_DRIVER_NAME")),
	username = os.getenv("DB_USERNAME"),
	password = os.getenv("DB_PASSWORD"),
	host = os.getenv("DB_HOST"),
	database = os.getenv("DB_DATABASE"),
	query = {"sslmode":"require"}
)

engine = create_engine(connection_string)

app = Flask(__name__)
app.config["secret_key"] = os.getenv("DB_SECRET_KEY")
app.config["SQLALCHEMY_DATABASE_URI"] = connection_string

db = SQLAlchemy(app)
ma = Marshmallow(app)
