import json
from xgboost import XGBRegressor
from lightgbm import LGBMRegressor
from catboost import CatBoostRegressor
from sklearn.model_selection import KFold, cross_val_score
from sklearn.datasets import fetch_california_housing
from pymongo import MongoClient
from datetime import datetime
import pandas as pd
import socket
import time
import os


def save_to_mongo(df, model: str):
    client = MongoClient(os.environ['mongoService'])
    db = client["test"]
    db[model].insert_many(df.to_dict("records"))
    record_count = db[model].count_documents({})
    print(f"Model Saved to DB. Doc Count {record_count}")


def make_results_df(regressor, results, model, timer):
    """
    Build a dataframe for the training results.
    """
    local_result = pd.DataFrame([regressor.get_params()])
    local_result["result_mean"] = results.mean()
    local_result["model_type"] = model
    local_result["host_name"] = socket.gethostname()
    local_result["date_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    local_result["execute_time"] = timer
    return local_result


def training_pipeline(regressor, fold: int, model: str) -> pd.DataFrame:
    """Run the regressor "fold" times
        Output the result to a DF

    Parameters
    ----------
    regressor : XGBRegressor, LGBMRegressor, or CatBoostRegressor
        A regressor object with params already feed in
    fold : int
        Number of times the data should be split, train, and evaluated.
    model : str
        Name of the model. 'xgboost', 'lightgbm', or 'catboost'

    Returns
    -------
    local_result: pd.DataFrame
        Result dataframe
    """
    X, y = fetch_california_housing(return_X_y=True)
    kfold = KFold(n_splits=fold)
    tic = time.perf_counter()
    results = cross_val_score(regressor, X, y, cv=kfold, n_jobs=1)
    timer = round(time.perf_counter() - tic, 4)
    local_result = make_results_df(regressor, results, model, timer)
    return local_result


def trainer(param_grids: list, fold=5):
    print(f"length of param grid received {len(param_grids)}")
    for param in param_grids:
        model = param.pop("model")
        if model == "xgboost":
            regressor = XGBRegressor(objective="reg:squarederror", **param)
            local_result = training_pipeline(regressor, fold, model)
            save_to_mongo(local_result, model)
        elif model == "lightgbm":
            regressor = LGBMRegressor(**param)
            local_result = training_pipeline(regressor, fold, model)
            save_to_mongo(local_result, model)
        elif model == "catboost":
            regressor = CatBoostRegressor(**param)
            local_result = training_pipeline(regressor, fold, model)
            save_to_mongo(local_result, model)
        else:
            print(f"model {model} is not supported")
