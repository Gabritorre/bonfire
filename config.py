from os import getenv, getpid
from threading import Lock, get_native_id
from random import randint
from datetime import datetime, timezone
from dotenv import load_dotenv
from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from sqlalchemy import URL, create_engine
from functools import wraps

load_dotenv()

class Snowflake:
	def __init__(self):
		self.__generated_snowflakes = {}
		self.__diff_mask = (1 << 42) - 1 # 42 bit mask
		self.__worker_mask = (1 << 5) - 1 # 5 bit mask
		self.__increment_mask = (1 << 12) - 1 # 12 bit mask
		self.__epoch = 1719792000000.0 # 01/07/2024 unix time in ms
		self.__lock = Lock()

	def generate(self) -> int:
		current_date = datetime.now(timezone.utc).timestamp() * 1000
		time_diff = int(current_date - self.__epoch) & self.__diff_mask
		process_id = getpid() & self.__worker_mask
		thread_id = get_native_id() & self.__worker_mask

		snowflake = (time_diff << 10) | (process_id << 5) | thread_id
		with self.__lock:
			if snowflake in self.__generated_snowflakes:
				self.__generated_snowflakes[snowflake] += 1
				snowflake = (snowflake << 12) | (self.__generated_snowflakes[snowflake] & self.__increment_mask)
			else:
				self.__generated_snowflakes[snowflake] = 0
				snowflake = snowflake << 12

		rand = randint(0, (1 << 64) - 1) # 64 bit random integer (at most)
		return (snowflake << 64) | rand

	def creation_date(self, sf: int) -> datetime:
		extracted_time_diff = sf >> 86
		return datetime.fromtimestamp((extracted_time_diff+self.__epoch)/1000, tz=timezone.utc)

snowflake = Snowflake()

def safeguard(func):
	@wraps(func)
	def wrapper():
		try:
			return func()
		except Exception as e:
			print("-"*50 + f"\n\033[0;31mError on \033[4m{func.__name__}\033[0m: {e}\033[0m\n" + "-"*50)
			db.session.rollback()
			return jsonify({"error": "something went wrong"})
	return wrapper

connection_string = URL.create(
	str(getenv("DB_DRIVER_NAME")),
	username = getenv("DB_USERNAME"),
	password = getenv("DB_PASSWORD"),
	host = getenv("DB_HOST"),
	database = getenv("DB_DATABASE"),
	query = {"sslmode": "require"}
)

engine = create_engine(connection_string)

app = Flask(__name__)
app.config["secret_key"] = getenv("DB_SECRET_KEY")
app.config["SQLALCHEMY_DATABASE_URI"] = connection_string
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {"pool_pre_ping": True}
app.config["UPLOAD_FOLDER"] = "media"

db = SQLAlchemy(app)
ma = Marshmallow(app)
