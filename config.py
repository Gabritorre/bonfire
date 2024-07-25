from sqlalchemy import URL, create_engine
from sqlalchemy.orm import sessionmaker
from flask_sqlalchemy import SQLAlchemy
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
local_session = sessionmaker(autocommit = False, autoflush = False, bind = engine)

db = SQLAlchemy()