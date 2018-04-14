from flask import Flask
from flask import render_template
from flask import request
from flask import jsonify
import requests
# import pandas as pd

app = Flask(__name__)

API_KEY='0fce4f7d72de5c934ab7dc9691c6447b'
SECONDS_PER_DAY=86400

@app.route("/")
def homepage():
    genedge = "GEN.EDGE"
    team_members = "Charlie Fitzgerald, Geoff Hancock, Ian Kitchens, Harrison Li, Aaron Newman"
    data = pd.read_csv("All_Data_Hourly_8760_for_input.csv")
    columns = ["DateTime", "DayOfWeek", "DayType", "Wholesale", "Retail", "WholewVariance", "RetailwVariance",
               "BuildingLoad", "WindProduction", "PVgeneration", "GHI"]
    data.columns = columns
    buildingData = data[["DateTime", "BuildingLoad"]]
    buildingData = buildingData.to_json(orient="records")
    windData = data[["DateTime", "WindProduction"]]
    windData = windData.to_json(orient="records")
    pvData = data[["DateTime", "PVgeneration"]]
    pvData = pvData.to_json(orient="records")
    netData = data["BuildingLoad"] - data["PVgeneration"] - data["WindProduction"]
    netData = netData.to_json(orient="records")
    # print(graphData)
    # print(data.head())
    # graphData = data[]
    variables = {"team": genedge, "members": team_members,
                 "building_data": buildingData,
                 "wind_data": windData,
                 "pv_data": pvData,
                 "net_data": netData
                 }
    return render_template("home.html", **variables)

@app.route("/weather_forecast")
def get_forecast():
    latitude = request.args.get('latitude')
    longitude = request.args.get('longitude')
    response = jsonify(requests.get('https://api.darksky.net/forecast/{}/{},{}'.format(API_KEY, latitude, longitude)).json()['hourly']['data'])
    return response

@app.route("/weather_historical")
def get_historical():
    latitude = request.args.get('latitude')
    longitude = request.args.get('longitude')
    unix_time = int(request.args.get('unix_time'))
    aggregate_response = []
    for i in range(0, 8):
        aggregate_response = aggregate_response + requests.get('https://api.darksky.net/forecast/{}/{},{},{}'.format(API_KEY, latitude, longitude, unix_time)).json()['hourly']['data']
        unix_time = unix_time + SECONDS_PER_DAY
    return jsonify(aggregate_response)
    
if __name__ == "__main__":
    # data = pd.read_csv("All_Data_Hourly_8760_for_input.csv")
    # print(data.head())
    # print(list(data))
    app.run()