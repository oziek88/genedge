from flask import Flask
from flask import render_template
from flask import request
from flask import jsonify
import requests
app = Flask(__name__)

API_KEY='0fce4f7d72de5c934ab7dc9691c6447b'

@app.route("/")
def homepage():
    genedge = "GEN.EDGE"
    team_members = "Charlie Fitzgerald, Geoff Hancock, Ian Kitchens, Harrison Li, Aaron Newman"
    variables = {"team": genedge, "members": team_members}
    return render_template("home.html", **variables)

@app.route("/weather_forecast")
def get_forecast():
    latitude = request.args.get('latitude')
    longitude = request.args.get('longitude')
    response = jsonify(requests.get('https://api.darksky.net/forecast/{}/{},{}'.format(API_KEY, latitude, longitude)).json()['hourly'])
    return response

@app.route("/weather_historical")
def get_historical():
    latitude = request.args.get('latitude')
    longitude = request.args.get('longitude')
    unix_time = request.args.get('unix_time')
    response = jsonify(requests.get('https://api.darksky.net/forecast/{}/{},{},{}'.format(API_KEY, latitude, longitude, unix_time)).json()['hourly'])
    return response
    
if __name__ == "__main__":
    app.run()