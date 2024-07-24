from sqlalchemy import URL, create_engine
from dotenv import load_dotenv
import os

load_dotenv()

connection_string = URL.create(
	os.getenv("DB_DRIVER_NAME"),
	username = os.getenv("DB_USERNAME"),
	password = os.getenv("DB_PASSWORD"),
	host = os.getenv("DB_HOST"),
	database = os.getenv("DB_DATABASE"),
	query = {"sslmode":"require"}
)

engine = create_engine(connection_string)
