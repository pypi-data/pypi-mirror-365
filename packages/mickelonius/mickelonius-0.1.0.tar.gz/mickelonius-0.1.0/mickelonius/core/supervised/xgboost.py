import xgboost as xgb
import numpy as np

from mickelonius.sys.nvidia.utils import get_gpu_usage


def test_xgboost_regression():
    # Generate dummy dataset
    X = np.random.rand(1000, 10)
    y = np.random.randint(2, size=1000)

    # Convert to DMatrix format
    dtrain = xgb.DMatrix(X, label=y)


    params = {
        "device": "cuda",
        "objective": "binary:logistic",
        "eval_metric": "logloss"
    }

    bst = xgb.train(params, dtrain, num_boost_round=100)
    get_gpu_usage()
