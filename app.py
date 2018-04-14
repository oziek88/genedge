from flask import Flask
from flask import render_template
app = Flask(__name__)
import pandas as pd

@app.route("/")
def homepage():
    genedge = "GEN.EDGE"
    team_members = "Charlie Fitzgerald, Geoff Hancock, Ian Kitchens, Harrison Li, Aaron Newman"
    data = pd.read_csv("All_Data_Hourly_8760.xlsx")
    graphData = data[["Date Time (Start)", "Wholesale ($/kWh)"]]
    graphData = graphData.to_json()
    print(data.head())
    # graphData = data[]
    variables = {"team": genedge, "members": team_members, "chart_data": graphData}
    return render_template("home.html", **variables)

# @app.route("/", )

if __name__ == "__main__":
    # data = pd.read_csv("All_Data_Hourly_8760_for_input.csv")
    # print(data.head())
    # print(list(data))
    app.run()