FROM python:3.12-slim-bullseye

LABEL Description="python-flask-sqlalchemy"

WORKDIR /app

COPY . /app

RUN apt update && apt install libmagic1 -y  #dependency of python-magic

RUN pip install -r requirements.txt

RUN echo 'DB_DRIVER_NAME="postgresql"' >> .env && \
    echo 'DB_USERNAME="postgres"' >> .env && \
    echo 'DB_PASSWORD="1234"' >> .env && \
    echo 'DB_HOST="db"' >> .env && \
    echo 'DB_PORT="5432"' >> .env && \
    echo 'DB_DATABASE="postgres"' >> .env && \
    echo 'DB_SECRET_KEY="random_generated_string"' >> .env && \
    echo 'DB_DEBUG="1"' >> .env

EXPOSE 5000

CMD ["sh", "-c", "python create_database.py && flask run --debug --host=0.0.0.0"]

