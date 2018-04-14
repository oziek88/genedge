import time
import numpy as np
import os
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from datetime import datetime
from sklearn.model_selection import KFold
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.decomposition import PCA
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
from typing import Union

defaultBoostedRegressorParams = {
    'loss': 'ls',
    'learning_rate': .05,
    'subsample': .7,
    'verbose': 1,
    'max_depth': 5,
    'n_estimators': 1000
}
defaultTrainingData = "SOMEPATH"
defaultTestingData = "SOMEPATH"
defaultNewDataDir = "SOMEPATH"

def adjustedRScore(rSquared: float, numDataPts: int, numPredictors: int) -> float:
    numerator = (1 - rSquared) * (numDataPts - 1)
    denominator = numDataPts - numPredictors - 1
    return 1 - numerator / denominator

class Predictor:
    """based on: https://www.kaggle.com/hguimaraes/pysolar-dataset-exploration-and-train-test
    NOTE: maybe need to add in other sources so that it outputs: Wind speed, air temp, dhi, dni, ghi"""
    def __init__(self, modelParams:dict=None,
                 trainingDataDir: str=None,
                 testingDataDir: str=None,
                 newDataDir: str=None):
        self.trainingDir = trainingDataDir
        self.testingDir = testingDataDir
        self.newDataDir = newDataDir
        self.params = modelParams
        self.model = GradientBoostingRegressor(**modelParams)
        self.daysBack = 7

    def _uploadData(self, train: int, path: str) -> pd.DataFrame:
        """upload data that lives at the relative path of PATH and abs. path of either self.trainingDir + path
        or self.testingDir + path.
        if TRAIN == True then use self.trainingDir, otherwise use self.testingDir"""
        data = None
        if train == 0:
            data = pd.read_csv(os.path.join(self.trainingDir, path))
        elif train == 1:
            data = pd.read_csv(os.path.join(self.testingDir, path))
        elif train == 2:
            data = pd.read_csv(os.path.join(self.newDataDir, path))
        return data

    def train(self, data: pd.DataFrame, labelData: Union[pd.DataFrame, str]=None) -> None:
        if isinstance(labelData, str):
            Xtrain = data.drop([labelData], axis=1)
            Ytrain = data[[labelData]]
        else:
            Ytrain = labelData
            Xtrain = data
        self.model.fit(Xtrain, Ytrain)

    def test(self, data: pd.DataFrame, labelData: Union[pd.DataFrame, str]=None) -> tuple:
        """returns tuple (RMSE, adjusted R squared, predictions, true values)"""
        if isinstance(labelData, str):
            Xtest = data.drop([labelData], axis=1)
            Ytest = data[[labelData]]
        else:
            Ytest = labelData
            Xtest = data
        numDataPts = len(Xtest)
        numParameters = len(Xtest.iloc[0])
        Ypredictions = self.model.predict(Xtest)
        return mean_squared_error(Ytest, Ypredictions), \
               adjustedRScore(r2_score(Ytest, Ypredictions), numDataPts, numParameters), \
               Ypredictions, \
               Ytest

    def transformData(self, data: pd.DataFrame, goalLabel: str):
        """

        :return: a pandas DataFrame object that is in the format for the model to be trained, where one column
        is the goal and the rest are input parameters. Rows / indices are timestamps
        """
        count = 0
        newColumns = ["dayBack" + str(count) for count in range(1, self.daysBack+1)]
        for i, row in data.iterrows():
            if count < 6:
                count += 1
                pass
            else:
                for days in range(self.daysBack):




    def predict(self, newData: Union[str, pd.DataFrame]) -> np.ndarray:
        data = newData
        if isinstance(newData, str):
            data = self._uploadData(2, newData)
        return self.model.predict(data)

    def assignParams(self, params:dict) -> None:
        self.params = params

if __name__ == "__main__":
    """
    """
    predictor = Predictor(modelParams=defaultBoostedRegressorParams,
                          trainingDataDir=defaultTrainingData,
                          testingDataDir=defaultTestingData,
                          newDataDir=defaultNewDataDir)
    headers = ["SOME HEADERS"]
    trainingData = pd.read_table(os.path.join(defaultTrainingData, "SOMEFILE"),
                                 delim_whitespace=True, header=None, names=headers)
    # DROP all columns except ones that we should be able to get from APIs like OpenWeatherMap / AccuWeather
    # NOTE: CRNS doesn't have cloud cover, that would be nice to have
    X = trainingData[["SOME HEADERS"]]
    y = trainingData[["SOMEGOAL"]]

    Xtrain, Xtest, Ytrain, Ytest = train_test_split(X, y, test_size=0.25)
    predictor.train(Xtrain, Ytrain)
    MSE, adjRScore, predictions, trueValues = predictor.test(Xtest, Ytest)
    print(adjRScore)
    # print(trainingData.head())
    # print(list(trainingData))
