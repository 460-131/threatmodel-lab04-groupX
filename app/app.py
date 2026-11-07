import sqlite3
import requests
from flask import Flask, request, session
app = Flask(__name__)
app.secret_key = &quot;urbanbike-dev-key&quot;
LOCK_API_KEY = &quot;lock-key-0001&quot;
DB = &quot;urbanbike.db&quot;
def db():
return sqlite3.connect(DB)
@app.route(&quot;/login&quot;, methods=[&quot;POST&quot;])
def login():
u = request.form[&quot;username&quot;]
p = request.form[&quot;password&quot;]
row = db().execute(&quot;SELECT id FROM riders WHERE name=&#39;%s&#39; AND pw=&#39;%s&#39;&quot; % (u, p)).fetchone()
if row:
session[&quot;uid&quot;] = row[0]
return (&quot;OK&quot;, 200) if row else (&quot;Invalid&quot;, 401)
@app.route(&quot;/unlock&quot;, methods=[&quot;POST&quot;])
def unlock():
try:
requests.post(&quot;https://locks.example.com/unlock&quot;,
data={&quot;bike&quot;: request.form[&quot;bike_id&quot;], &quot;key&quot;: LOCK_API_KEY})
return &quot;Unlocked&quot;
except Exception as e:
return str(e), 500
@app.route(&quot;/rides&quot;)
def rides():
rid = request.args.get(&quot;rider_id&quot;)
rows = db().execute(f&quot;SELECT bike, start, cost FROM rides WHERE rider_id={rid}&quot;).fetchall()
return str(rows)
@app.route(&quot;/refund&quot;, methods=[&quot;POST&quot;])
def refund():
db().execute(&quot;UPDATE rides SET cost=0 WHERE id=?&quot;, (request.form[&quot;ride_id&quot;],))
return &quot;Refunded&quot;
@app.route(&quot;/health&quot;)
def health():
return &quot;ok&quot;
if __name__ == &quot;__main__&quot;:
app.run(host=&quot;0.0.0.0&quot;, debug=True)
