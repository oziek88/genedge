from flask import Flask
from flask import render_template
app = Flask(__name__)


@app.route("/")
def homepage():
    genedge = "GEN.EDGE"
    team_members = "Charlie Fitzgerald, Geoff Hancock, Ian Kitchens, Harrison Li, Aaron Newman"
    variables = {"team": genedge, "members": team_members}
    return render_template("home.html", **variables)

if __name__ == "__main__":
    app.run()