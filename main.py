from flask import (Flask, render_template, session, redirect, 
                   url_for, session, request, jsonify, send_from_directory)
from flask_wtf import FlaskForm
from wtforms import SelectField, SubmitField
from wtforms.validators import DataRequired
import Get, rewriting, plot

app = Flask(__name__)
app.config['SECRET_KEY'] = 'mysecretkey'

class InfoForm(FlaskForm):
    cities = [("--Choose your city--", "--Choose your city--")] + Get.GetCities()
    
    city = SelectField("Choose your city: ", choices = cities)
    street = SelectField("Choose your street: ", choices = [])
    pollutant = SelectField("Choose pollutant: ", choices = [])
    date = SelectField("Choose date: ", choices = [])
    type = SelectField("Choose type of data: ", choices = [])

@app.route("/", methods = ["GET", "POST"])
def index():
    rewriting.FinalStats()
    form = InfoForm()
    
    dates = Get.GetDate()
    dates.insert(0,("--Choose a date--", "--Choose a date--"))
    dates.insert(1,("Last 3 days","Last 3 days"))
    dates.insert(2,("Last 7 days","Last 7 days"))

    form.date.choices = dates
    form.street.choices = [("--Choose station--", "--Choose station--")]
    form.pollutant.choices = [("--Choose pollutant--","--Choose pollutant--")]
    form.type.choices = [("--Choose type of data--", "--Choose type of data--")]

    if request.method == "POST":

        session["city"] = form.city.data
        session["street"] = form.street.data
        session["pollutant"] = form.pollutant.data
        session["date"] = form.date.data
        session["type"] = form.type.data
        FinalData = plot.GetFinalData(session["city"], session["street"],
                                     session["pollutant"], session["date"],
                                     session["type"])
        if FinalData == None:
            return render_template("plot.html", data = FinalData, url = 'static/images/newplot.png')
        else:
            return render_template("error.html", data = FinalData, url = 'static/images/newplot.png')

    return render_template("index.html", form = form )

@app.route("/street/<city>")
def street(city):
    streets = Get.GetStreets(city)
    streets.insert(0,("--Choose street--", "--Choose street--"))
    streetList = []

    for street in streets:
        streetObj = {}
        streetObj["id"] = street[0]
        streetObj["name"] = street[1]
        streetList.append(streetObj)

    return jsonify({"streets": streetList})

@app.route("/pollutant/<street>")
def pollutant(street):
    pollutants = Get.GetPollutant1(street)
    pollutants.insert(0,("--Choose pollutant--", "--Choose pollutant--"))
    pollutantList = []

    for pollutant in pollutants:
        pollutantObj = {}
        pollutantObj["id"] = pollutant[0]
        pollutantObj["name"] = pollutant[1]
        pollutantList.append(pollutantObj)

    return jsonify({"pollutants": pollutantList})

@app.route("/type/<date>")
def type(date):
    types = Get.GetType(date)
    typeList = []

    for type in types:
        typeObj = {}
        typeObj["id"] = type[0]
        typeObj["name"] = type[1]
        typeList.append(typeObj)

    return jsonify({"types": typeList})
##NEW
@app.errorhandler(500)
def error_handler():
    return redirect(url_for("/"))



if __name__ == '__main__':
    app.run(debug=True)
    