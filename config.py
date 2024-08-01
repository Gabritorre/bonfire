import os
from datetime import datetime, timezone
from threading import Lock, get_native_id
from random import randint
from dotenv import load_dotenv
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from sqlalchemy import URL, create_engine

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
		process_id = os.getpid() & self.__worker_mask
		thread_id = get_native_id() & self.__worker_mask

		snowflake = (time_diff << (10)) | (process_id << (5)) | thread_id
		with self.__lock:
			if snowflake in self.__generated_snowflakes:
				self.__generated_snowflakes[snowflake] += 1
				snowflake = (snowflake << 12) | (self.__generated_snowflakes[snowflake] & self.__increment_mask)
			else:
				self.__generated_snowflakes[snowflake] = 0
				snowflake = (snowflake << 12)

		rand = randint(0, (2**64)-1) # 64 bit
		return (snowflake << 64) | rand

	def creation_date(self, s: int) -> datetime:
		extracted_diff = (s >> (86)) & self.__diff_mask
		return datetime.fromtimestamp((extracted_diff+self.__epoch)/1000, tz=timezone.utc)

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
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {"pool_pre_ping": True}

db = SQLAlchemy(app)
ma = Marshmallow(app)
