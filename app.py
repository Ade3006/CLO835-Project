import os
import logging
from flask import Flask, render_template
import pymysql

app = Flask(__name__)

logging.basicConfig(level=logging.INFO)

DBHOST = os.getenv("DBHOST", "mysql")
DBPORT = int(os.getenv("DBPORT", "3306"))
DBUSER = os.getenv("DBUSER", "root")
DBPWD = os.getenv("DBPWD", "password")
DATABASE = os.getenv("DATABASE", "employees")

HEADER_NAME = os.getenv("HEADER_NAME", "Ade")
S3_BUCKET = os.getenv("S3_BUCKET", "")
S3_KEY = os.getenv("S3_KEY", "")
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")


def build_public_s3_url() -> str:
    if not S3_BUCKET or not S3_KEY:
        logging.warning("S3 bucket or key not set.")
        return ""

    if AWS_REGION == "us-east-1":
        image_url = f"https://{S3_BUCKET}.s3.amazonaws.com/{S3_KEY}"
    else:
        image_url = f"https://{S3_BUCKET}.s3.{AWS_REGION}.amazonaws.com/{S3_KEY}"

    logging.info(f"Using public S3 image URL: {image_url}")
    return image_url


def get_db_connection():
    return pymysql.connect(
        host=DBHOST,
        user=DBUSER,
        password=DBPWD,
        database=DATABASE,
        port=DBPORT,
        connect_timeout=5
    )


@app.route("/")
def home():
    bg_image = build_public_s3_url()
    return render_template("index.html", header_name=HEADER_NAME, bg_image=bg_image)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=81)