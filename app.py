import os
import logging
from flask import Flask, render_template
import boto3
from botocore.exceptions import ClientError
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
LOCAL_IMAGE_DIR = "static/images"
LOCAL_IMAGE_FILE = "background.jpg"
LOCAL_IMAGE_PATH = f"{LOCAL_IMAGE_DIR}/{LOCAL_IMAGE_FILE}"

def download_background():
    if not S3_BUCKET or not S3_KEY:
        logging.warning("S3 bucket or key not set.")
        return

    os.makedirs(LOCAL_IMAGE_DIR, exist_ok=True)
    logging.info(f"Background image S3 path: s3://{S3_BUCKET}/{S3_KEY}")

    s3 = boto3.client("s3", region_name=os.getenv("AWS_REGION", "us-east-1"))
    try:
        s3.download_file(S3_BUCKET, S3_KEY, LOCAL_IMAGE_PATH)
        logging.info(f"Downloaded background image to {LOCAL_IMAGE_PATH}")
    except ClientError as e:
        logging.error(f"Failed to download image from S3: {e}")

def get_db_connection():
    return pymysql.connect(
        host=DBHOST,
        user=DBUSER,
        password=DBPWD,
        database=DATABASE,
        port=DBPORT
    )

@app.route("/")
def home():
    if not os.path.exists(LOCAL_IMAGE_PATH):
        download_background()

    image_exists = os.path.exists(LOCAL_IMAGE_PATH)
    image_path = f"/{LOCAL_IMAGE_PATH}" if image_exists else ""
    return render_template("index.html", header_name=HEADER_NAME, bg_image=image_path)

if __name__ == "__main__":
    download_background()
    app.run(host="0.0.0.0", port=81)
