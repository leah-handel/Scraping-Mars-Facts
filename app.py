from flask import Flask, render_template, redirect
from flask_pymongo import PyMongo
import scrape_mars

app = Flask(__name__)

app.config["MONGO_URI"] = "mongodb://localhost:27017/phone_app"
mongo = PyMongo(app)

@app.route("/")
def home():
    mars_content = mongo.db.mars.find_one()
    return render_template("index.html", mars=mars_content)

@app.route("/scrape")
def scrape():
    mars_data = mongo.db.mars
    mars_updates = scrape_mars.scrape()
    mars_data.update({}, mars_updates, upsert=True)
    return redirect("/", code=302)

if __name__ == "__main__":
    app.run(debug=True)