import json
import urllib.request

from flask import Flask, render_template, redirect, url_for, request
from flask_wtf import FlaskForm
from requests.exceptions import ConnectionError
from wtforms import IntegerField, SelectField, StringField, FloatField
from wtforms.validators import DataRequired

class ClientDataForm(FlaskForm):
    full_sq = FloatField('Full area of apartment in square meters', validators=[DataRequired()])
    num_room = IntegerField('Number of rooms', validators=[DataRequired()])
    build_year = IntegerField('Year the house was built', validators=[DataRequired()])


app = Flask(__name__)
app.config.update(
    CSRF_ENABLED=True,
    SECRET_KEY='you-will-never-guess',
)

def get_prediction(full_sq, num_room, build_year):
    body = {'full_sq': full_sq,
            'num_room': num_room,
            'build_year': build_year}

    myurl = "http://0.0.0.0:8180/predict"
    req = urllib.request.Request(myurl)
    req.add_header('Content-Type', 'application/json; charset=utf-8')
    jsondata = json.dumps(body)
    jsondataasbytes = jsondata.encode('utf-8')   # needs to be bytes
    req.add_header('Content-Length', len(jsondataasbytes))
    #print (jsondataasbytes)
    response = urllib.request.urlopen(req, jsondataasbytes)
    return json.loads(response.read())['predictions']

@app.route("/")
def index():
    return render_template('index.html')


@app.route('/predicted/<response>')
def predicted(response):
    response = json.loads(response)
    print(response)
    return render_template('predicted.html', response=response)


@app.route('/predict_form', methods=['GET', 'POST'])
def predict_form():
    form = ClientDataForm()
    data = dict()
    if request.method == 'POST':
        data['full_sq'] = request.form.get('full_sq')
        data['num_room'] = request.form.get('num_room')
        data['build_year'] = request.form.get('build_year')


        try:
            response = str(get_prediction(data['full_sq'],
                                      data['num_room'],
                                      data['build_year']))
            print(response)
        except ConnectionError:
            response = json.dumps({"error": "ConnectionError"})
        return redirect(url_for('predicted', response=response))
    return render_template('form.html', form=form)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8181, debug=True)
