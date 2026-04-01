from flask import Flask, render_template, request
from pymysql import connections
import os
import random
import argparse

app = Flask(__name__)

DBHOST = os.environ.get("DBHOST") or "localhost"
DBUSER = os.environ.get("DBUSER") or "root"
DBPWD = os.environ.get("DBPWD") or "pw"
DATABASE = os.environ.get("DATABASE") or "employees"
DBPORT = int(os.environ.get("DBPORT") or 3306)

HEADER_NAME = os.environ.get("HEADER_NAME") or "Ade"
S3_BUCKET = os.environ.get("S3_BUCKET")
S3_KEY = os.environ.get("S3_KEY")
AWS_REGION = os.environ.get("AWS_REGION") or "us-east-1"
APP_COLOR = os.environ.get("APP_COLOR") or "lime"

table = "employee"

color_codes = {
    "red": "#e74c3c",
    "green": "#16a085",
    "blue": "#89CFF0",
    "blue2": "#30336b",
    "pink": "#f4c2c2",
    "darkblue": "#130f40",
    "lime": "#C1FF9C",
}

COLOR = APP_COLOR if APP_COLOR in color_codes else "lime"


def get_db_connection():
    return connections.Connection(
        host=DBHOST,
        port=DBPORT,
        user=DBUSER,
        password=DBPWD,
        db=DATABASE
    )


def get_background_image_url():
    if S3_BUCKET and S3_KEY:
        return f"https://{S3_BUCKET}.s3.{AWS_REGION}.amazonaws.com/{S3_KEY}"
    return None


@app.route("/", methods=["GET", "POST"])
def home():
    return render_template(
        "addemp.html",
        color=color_codes[COLOR],
        bg_image=get_background_image_url(),
        header_name=HEADER_NAME
    )


@app.route("/about", methods=["GET", "POST"])
def about():
    return render_template(
        "about.html",
        color=color_codes[COLOR],
        bg_image=get_background_image_url(),
        header_name=HEADER_NAME
    )


@app.route("/addemp", methods=["POST"])
def AddEmp():
    emp_id = request.form["emp_id"]
    first_name = request.form["first_name"]
    last_name = request.form["last_name"]
    primary_skill = request.form["primary_skill"]
    location = request.form["location"]

    insert_sql = "INSERT INTO employee VALUES (%s, %s, %s, %s, %s)"
    db_conn = get_db_connection()
    cursor = db_conn.cursor()

    try:
        cursor.execute(insert_sql, (emp_id, first_name, last_name, primary_skill, location))
        db_conn.commit()
        emp_name = first_name + " " + last_name
    finally:
        cursor.close()
        db_conn.close()

    return render_template(
        "addempoutput.html",
        name=emp_name,
        color=color_codes[COLOR],
        bg_image=get_background_image_url(),
        header_name=HEADER_NAME
    )


@app.route("/getemp", methods=["GET", "POST"])
def GetEmp():
    return render_template(
        "getemp.html",
        color=color_codes[COLOR],
        bg_image=get_background_image_url(),
        header_name=HEADER_NAME
    )


@app.route("/fetchdata", methods=["GET", "POST"])
def FetchData():
    emp_id = request.form["emp_id"]
    output = {}

    select_sql = "SELECT emp_id, first_name, last_name, primary_skill, location FROM employee WHERE emp_id=%s"
    db_conn = get_db_connection()
    cursor = db_conn.cursor()

    try:
        cursor.execute(select_sql, (emp_id,))
        result = cursor.fetchone()

        if result:
            output["emp_id"] = result[0]
            output["first_name"] = result[1]
            output["last_name"] = result[2]
            output["primary_skills"] = result[3]
            output["location"] = result[4]
        else:
            output["emp_id"] = "Not found"
            output["first_name"] = ""
            output["last_name"] = ""
            output["primary_skills"] = ""
            output["location"] = ""
    finally:
        cursor.close()
        db_conn.close()

    return render_template(
        "getempoutput.html",
        id=output["emp_id"],
        fname=output["first_name"],
        lname=output["last_name"],
        interest=output["primary_skills"],
        location=output["location"],
        color=color_codes[COLOR],
        bg_image=get_background_image_url(),
        header_name=HEADER_NAME
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=81, debug=True)