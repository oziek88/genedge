from flask import Flask
from flask import render_template
from flask import request
from flask import jsonify
import requests
import pandas as pd
import model

app = Flask(__name__)

API_KEY='0fce4f7d72de5c934ab7dc9691c6447b'
SECONDS_PER_DAY=86400

@app.route("/")
def homepage():
    genedge = "GEN.EDGE"
    team_members = "Charlie Fitzgerald, Geoff Hancock, Ian Kitchens, Harrison Li, Aaron Newman"
    data = pd.read_csv("All_Data_Hourly_8760_for_input.csv")
    columns = ["DateTime", "DayOfWeek", "DayType", "Wholesale", "Retail", "WholewVariance", "RetailwVariance",
               "BuildingLoad", "WindProduction", "PVgeneration", "GHI", "apparentTemperature",
               "cloudCover", "precipIntensity", "windSpeed"]
    trainColumns = ["DayOfWeek", "Wholesale", "Retail", "WholewVariance", "RetailwVariance",
               "BuildingLoad", "WindProduction", "PVgeneration", "GHI", "apparentTemperature",
               "cloudCover", "precipIntensity", "windSpeed"]
    data.columns = columns
    buildingData = data[["DateTime", "BuildingLoad"]]
    buildingData = buildingData.to_json(orient="records")
    windData = data[["DateTime", "WindProduction"]]
    windData = windData.to_json(orient="records")
    pvData = data[["DateTime", "PVgeneration"]]
    pvData = pvData.to_json(orient="records")
    data['netLoad'] = data["BuildingLoad"] - data["PVgeneration"] - data["WindProduction"]
    netData = data[["DateTime", "netLoad"]]
    netData = netData.to_json(orient="records")
    buildingPredictor = model.Predictor(model.defaultBoostedRegressorParams)
    trainData = pd.read_csv("training.csv")
    trainData.columns = trainColumns
    relevantColumns = ["BuildingLoad", "apparentTemperature", "cloudCover", "precipIntensity", "windSpeed"]
    relevantColumns2 = ["WindProduction", "apparentTemperature", "cloudCover", "precipIntensity", "windSpeed"]
    relevantColumns3 = ["PVgeneration", "apparentTemperature", "cloudCover", "precipIntensity", "windSpeed"]
    trainData1 = trainData[relevantColumns]
    trainData2 = trainData[relevantColumns2]
    trainData3 = trainData[relevantColumns3]
    buildingPredictor.train(trainData1, "BuildingLoad")
    windPredictor = model.Predictor(model.defaultBoostedRegressorParams)
    windPredictor.train(trainData2, "WindProduction")
    pvPredictor = model.Predictor(model.defaultBoostedRegressorParams)
    pvPredictor.train(trainData3, "PVgeneration")
    models = {"Wind": windPredictor, "Building": buildingPredictor, "pv": pvPredictor}
    forecastData = pd.read_csv("forecastcsv.csv")
    predictions = predictAWeek(forecastData, models)
    print(predictions.head())
    buildingPredictions = predictions[["Datetime", "BuildingLoad"]]
    buildingPredictions = buildingPredictions.to_json(orient='records')
    windPredictions = predictions[["Datetime", "WindProduction"]]
    windPredictions = windPredictions.to_json(orient='records')
    pvPredictions = predictions[["Datetime", "PVgeneration"]]
    pvPredictions = pvPredictions.to_json(orient='records')
    predictions["netLoad"] = predictions["BuildingLoad"] -  predictions["WindProduction"] - predictions["PVgeneration"]
    netPredictions = predictions[["Datetime", "netLoad"]]
    netPredictions = netPredictions.to_json(orient='records')
    # print(graphData)
    # print(data.head())
    # graphData = data[]
    # print(predictions.head())
    variables = {"team": genedge, "members": team_members,
                 "building_data": buildingData,
                 "wind_data": windData,
                 "pv_data": pvData,
                 "net_data": netData,
                 "forecast_building": buildingPredictions,
                 "forecast_wind": windPredictions,
                 "pvPredictions": pvPredictions,
                 "netLoad": netPredictions
                 }
    return render_template("home.html", **variables)

def predictAWeek(forecast, models):
    predictions = pd.DataFrame(columns=["WindProduction", "BuildingLoad", "PVgeneration"])
    for i, row in forecast.iterrows():
        predictedWeather = pd.DataFrame([[row["apparentTemperature"],row["cloudCover"], row["precipIntensity"], row["windSpeed"]]], columns=["apparentTemperature", "cloudCover", "precipIntensity", "windSpeed"])
        # print(predictedWeather)
        windprediction = models["Wind"].predict(predictedWeather)
        # print(type(windprediction))
        # print(windprediction[0])
        buildingprediction = models["Building"].predict(predictedWeather)
        pvprediction = models["pv"].predict(predictedWeather)
        tempFrame = pd.DataFrame([[windprediction[0], buildingprediction[0], pvprediction[0]]] , columns=["WindProduction", "BuildingLoad", "PVgeneration"])
        # print(tempFrame.head())
        predictions = predictions.append(tempFrame)
        # print(predictions.head())
    # print(len(predictions.index))
    print(predictions)
    predictions['Datetime'] = range(49)
    return predictions


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