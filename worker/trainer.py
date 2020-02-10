import json
from xgboost import XGBRegressor
from lightgbm import LGBMRegressor
from sklearn.model_selection import KFold, cross_val_score
from sklearn.datasets import fetch_california_housing
from pymongo import MongoClient
from datetime import datetime
import pandas as pd
import socket
import time


def save_to_mongo(df):
    client = MongoClient("mongodb://mongo-svc:27017/")
    db = client.test
    db.test.insert_many(df.to_dict("records"))
    print("Saved to MongoDB")


def result_to_df(regressor, results, model, timer):
    local_result = pd.DataFrame([regressor.get_params()])
    local_result["result_mean"] = results.mean()
    local_result["model_type"] = model
    local_result["host_name"] = socket.gethostname()
    local_result["date_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    local_result["execute_time"] = timer
    return local_result


def trainer(param_grids: list, folds=5):
    X, y = fetch_california_housing(return_X_y=True)
    output = pd.DataFrame()
    print(f"length of param grid received {len(param_grids)}")
    for param in param_grids:
        model = param.pop("model")
        if model == "xgboost":
            regressor = XGBRegressor(objective="reg:squarederror", **param)
            kfold = KFold(n_splits=folds)
            tic = time.perf_counter()
            results = cross_val_score(regressor, X, y, cv=kfold, n_jobs=1)
            timer = round(time.perf_counter() - tic, 4)
            local_result = result_to_df(regressor, results, model, timer)
            output = pd.concat([output, local_result])
        elif model == "lightgbm":
            regressor = LGBMRegressor(**param)
            kfold = KFold(n_splits=folds)
            tic = time.perf_counter()
            results = cross_val_score(regressor, X, y, cv=kfold, n_jobs=1)
            timer = round(time.perf_counter() - tic, 4)
            local_result = result_to_df(regressor, results, model, timer)
        elif model == "catboost":
            pass
        else:
            print(f"model {model} is not supported")
    save_to_mongo(output)
    print(output)
