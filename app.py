import json
from flask import Flask
from flask import render_template
from flask import jsonify
from readfunc import read_data
import datetime
app = Flask(__name__)

flag = True

with open('/home/pi/swan/ganga.json', 'r') as myfile:
    data = myfile.read()

# parse file
config = json.loads(data)


@app.route("/api")
def api_req():
    min = datetime.datetime.now().minute
    deadband = 0
    if min >= 58:
        deadband = (60-min)+2
    if min <= 2:
        deadband = 2-min
    if min >= 55 or min <= 5:
        return jsonify({"data": {}, "error": "device in busy state. Try after "+str(deadband) + "mins"})
    pl = ""
    global flag
    if flag is True:
        flag = False
        pl = read_data()
    else:
        return jsonify({"data": {}, "error": "device is busy in serving previous request. Try after 2 mins"})
    error = ""
    data = {}
    if(isinstance(pl, str)):
        error = pl
        flag = True
        return jsonify({"data": {}, "error": error})
    if(isinstance(pl, dict)):
        data = pl
        flag = True
        return jsonify({"data": pl["Fields"], "error": ""})


# @app.route("/")
# def home_req():
#     dt = datetime.datetime.now()
#     min = dt.minute
#     deadband = 0
#     if min >= 58:
#         deadband = (60-min)+2
#     if min <= 2:
#         deadband = 2-min
#     if min >= 55 or min <= 5:
#         return render_template("home.html", payload={}, error="device in busy state. Try after "+str(deadband) + "mins", date=dt.strftime('%B %d, %Y, %r'), siteId=config["displayName"])
#     pl = ""
#     global flag
#     if flag is True:
#         flag = False
#         pl = read_data()
#     else:
#         return render_template("home.html", payload={}, error="device is busy in serving previous request. Try after 2 mins", date=dt.strftime('%B %d, %Y, %r'), siteId=config["displayName"])
#     error = ""
#     data = {}
#     if(isinstance(pl, str)):
#         error = pl
#         flag = True
#         return render_template("home.html", payload=pl, error="", date=dt.strftime('%B %d, %Y, %r'), siteId=config["displayName"])
#     if(isinstance(pl, dict)):
#         data = pl
#         flag = True
#         return render_template("home.html", payload=pl["Fields"], error="", date=dt.strftime('%B %d, %Y, %r'), siteId=config["displayName"])


@app.route("/")
def loader_req():
    dt = datetime.datetime.now()
    return render_template("loader.html", date=dt.strftime('%B %d, %Y, %r'), siteId=config["displayName"])


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
