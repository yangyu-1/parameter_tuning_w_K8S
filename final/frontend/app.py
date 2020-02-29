from flask import Flask, render_template
from flask_pymongo import PyMongo
import pandas as pd

app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb://mongo-svc:27017/test"
mongo = PyMongo(app)


@app.route("/")
def hello_world():
    test = list(mongo.db.test.find({"model_type": "xgboost"}))
    df = pd.DataFrame(test)
    df.drop(labels="_id", axis=1, inplace=True)
    return render_template("index.html", data=df)


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")

