import os
import logging
import sqlite3
import requests
from functools import wraps
from flask import Flask, request, session

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", os.urandom(24))
LOCK_API_KEY = os.environ["LOCK_API_KEY"]
DB = "urbanbike.db"

log = logging.getLogger("audit")


def audit_log(action, **details):
    log.info("%s user=%s %s", action, session.get("uid"), details)


def require_auth(*roles):
    def deco(fn):
        @wraps(fn)
        def wrapper(*a, **k):
            if "uid" not in session or (roles and session.get("role") not in roles):
                return "Forbidden", 403
            return fn(*a, **k)
        return wrapper
    return deco


def db():
    return sqlite3.connect(DB)


@app.route("/login", methods=["POST"])
def login():
    u = request.form["username"]
    p = request.form["password"]
    row = db().execute(
        "SELECT id, role FROM riders WHERE name=? AND pw=?", (u, p)
    ).fetchone()
    if row:
        session["uid"] = row[0]
        session["role"] = row[1]
        return "OK", 200
    return "Invalid", 401


@app.route("/unlock", methods=["POST"])
@require_auth()
def unlock():
    try:
        requests.post(
            "https://locks.example.com/unlock",
            data={"bike": request.form["bike_id"], "key": LOCK_API_KEY},
            timeout=5,
        )
        return "Unlocked"
    except Exception:
        return "Lock service unavailable", 502


@app.route("/rides")
@require_auth()
def rides():
    rid = request.args.get("rider_id")
    if str(session["uid"]) != rid:
        return "Forbidden", 403
    rows = db().execute(
        "SELECT bike, start, cost FROM rides WHERE rider_id=?", (rid,)
    ).fetchall()
    return str(rows)


@app.route("/refund", methods=["POST"])
@require_auth("operator")
def refund():
    ride_id = request.form["ride_id"]
    db().execute("UPDATE rides SET cost=0 WHERE id=?", (ride_id,))
    audit_log("refund", ride_id=ride_id)
    return "Refunded"


@app.route("/health")
def health():
    return "ok"


if __name__ == "__main__":
    app.run(host="127.0.0.1", debug=False)
