from flask import Flask, jsonify, request
from flask_cors import CORS

from valexa.ploting.ploters import PloterData
from plotly.utils import PlotlyJSONEncoder
from valexa.ploting.utils import profile_to_dict

DEBUG = True

app = Flask(__name__)
app.config.from_object(__name__)
app.json_encoder = PlotlyJSONEncoder

CORS(app, resources={r'/*': {'origins': '*'}})

@app.route('/valexa_app/compute/', methods=['POST'])
def compute():
    response_object = {'status': 'success'}
    if request.method == 'POST':
        data = PloterData(
            request.files["file"].stream._file,
            tolerance_limit=int(request.form["tolerance"]),
            acceptance_limit=int(request.form["acceptance"])
        )
        response_object.update({
            "profiles": [profile_to_dict(p) for p in data.profiles],
        })
    
    return jsonify(response_object)


if __name__ == '__main__':
    app.run()
