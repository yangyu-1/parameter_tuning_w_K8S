import json
from xgboost import XGBRegressor
from sklearn.model_selection import KFold, cross_val_score


def trainer(param_grids: list, folds=10):
    for param in param_grids:
        model = i.pop("model")
        if model == "xgboost":
            regressor = XGBRegressor(objective="reg:squarederror", **param)
            kfold = KFold(n_splits=folds)
            results = cross_val_score(regressor, X, y, cv=kfold, n_jobs=-1)
            print(regressor)
            print(results.mean())
        elif model == "lightgbm":
            pass
        elif model == "catboost":
            pass
        else:
            print(f"model {model} is not supported")
