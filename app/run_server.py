# USAGE
# Start the server:
# 	python run_front_server.py
# Submit a request via Python:
#	python simple_request.py

# import the necessary packages
import dill
dill._dill._reverse_typemap['ClassType'] = type
import pickle
# Закостылил ошибку "AttributeError: Can't get attribute 'FeatureSelector' on <module '__main__' from..."
# Но можно было как-то более изящно, см. по ссылкам:
# https://www.stefaanlippens.net/python-pickling-and-dealing-with-attributeerror-module-object-has-no-attribute-thing.html
# https://stackoverflow.com/questions/27732354/unable-to-load-files-using-pickle-and-multiple-modules
from sklearn.base import BaseEstimator, TransformerMixin
import xgboost as xgb

import pandas as pd
import os

#import cloudpickle
import flask
import logging
from logging.handlers import RotatingFileHandler
from time import strftime

# initialize our Flask application and the model
app = flask.Flask(__name__)
model = None

handler = RotatingFileHandler(filename='app.log', maxBytes=100000, backupCount=10)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(handler)

class FeatureSelector(BaseEstimator, TransformerMixin):
    def __init__(self, column):
        self.column = column

    def fit(self, X, y=None):
        return self

    def transform(self, X, y=None):
        return X[self.column]
    
class NumberSelector(BaseEstimator, TransformerMixin):
    """
    Transformer to select a single column from the data frame to perform additional transformations on
    Use on numeric columns in the data
    """
    def __init__(self, key):
        self.key = key

    def fit(self, X, y=None):
        return self

    def transform(self, X):
        return X[[self.key]]
    
class OHEEncoder(BaseEstimator, TransformerMixin):
    def __init__(self, key):
        self.key = key
        self.columns = []

    def fit(self, X, y=None):
        self.columns = [col for col in pd.get_dummies(X, prefix=self.key).columns]
        return self

    def transform(self, X):
        X = pd.get_dummies(X, prefix=self.key)
        test_columns = [col for col in X.columns]
        for col_ in self.columns:
            if col_ not in test_columns:
                X[col_] = 0
        return X[self.columns]
    
class FitMedianNones(BaseEstimator, TransformerMixin):
    def __init__(self, key):
        self.key = key

    def fit(self, X, y=None):
        return self

    def transform(self, X):
        X.loc[X[self.key].isnull(), self.key] = X[self.key].median()
        return X[[self.key]]

class FitMedianNonesZeros(BaseEstimator, TransformerMixin):
    def __init__(self, key):
        self.key = key

    def fit(self, X, y=None):
        return self

    def transform(self, X):
        X.loc[(X[self.key] == 0) | (X[self.key].isnull()), self.key] = X[self.key].median()
        return X[[self.key]]

def load_model(model_path):
	# load the pre-trained model
	global model
	with open(model_path, 'rb') as f:
		model = dill.load(f)
	print(model)

# "/app/app/models" - см. dockerfile VOLUME, сюда должен с локального ПК подтянуться файл модели
modelpath = "/app/app/models/pipeline_xgb_v1.pkl"
load_model(modelpath)

@app.route("/", methods=["GET"])
def general():
	return """Welcome to prediction process. Please use 'http://<address>/predict' to POST"""

@app.route("/predict", methods=["POST"])
def predict():
	# initialize the data dictionary that will be returned from the
	# view
	data = {"success": False}
	dt = strftime("[%Y-%b-%d %H:%M:%S]")
	# ensure an image was properly uploaded to our endpoint
	if flask.request.method == "POST":

		full_sq, num_room, build_year = None, None, None
		request_json = flask.request.get_json()
		if request_json["full_sq"]:
			full_sq = request_json['full_sq']

		if request_json["num_room"]:
			num_room = request_json['num_room']

		if request_json["build_year"]:
			build_year = request_json['build_year']
		logger.info(f'{dt} Data: full_sq={full_sq}, num_room={num_room}, build_year={build_year}')
		try:
			preds = model.predict(pd.DataFrame({"full_sq": [full_sq],
												"num_room": [num_room],
												"build_year": [build_year]}))
		except AttributeError as e:
			logger.warning(f'{dt} Exception: {str(e)}')
			data['predictions'] = str(e)
			data['success'] = False
			return flask.jsonify(data)

		data["predictions"] = preds
		# indicate that the request was a success
		data["success"] = True

	# return the data dictionary as a JSON response
	return flask.jsonify(data)

# if this is the main thread of execution first load the model and
# then start the server
if __name__ == "__main__":
	print(("* Loading the model and Flask starting server..."
		"please wait until server has fully started"))
	port = int(os.environ.get('PORT', 8180))
	app.run(host='0.0.0.0', debug=True, port=port)