from flask import Flask
from flask import render_template
from flask import request
from flask import jsonify
import requests
import pandas as pd

app = Flask(__name__)

API_KEY='0fce4f7d72de5c934ab7dc9691c6447b'

@app.route("/")
def homepage():
    genedge = "GEN.EDGE"
    team_members = "Charlie Fitzgerald, Geoff Hancock, Ian Kitchens, Harrison Li, Aaron Newman"
    data = pd.read_csv("All_Data_Hourly_8760_for_input.csv")
    columns = ["DateTime", "DayOfWeek", "DayType", "Wholesale", "Retail", "WholewVariance", "RetailwVariance",
               "BuildingLoad", "WindProduction", "PVgeneration", "GHI"]
    data.columns = columns
    graphData = data[["DateTime", "Wholesale"]]
    graphData = graphData.to_json(orient="records")
    print(data.head())
    # graphData = data[]
    variables = {"team": genedge, "members": team_members, "chart_data": graphData}
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
    # data = pd.read_csv("All_Data_Hourly_8760_for_input.csv")
    # print(data.head())
    # print(list(data))
    app.run()