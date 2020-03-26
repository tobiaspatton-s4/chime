from collections import namedtuple
from datetime import datetime
from os import path
from tempfile import gettempdir
from zipfile import ZipFile

from flask import Flask, request, send_file

from penn_chime.models import SimSirModel
from penn_chime.parameters import Parameters
from penn_chime.utils import RateLos

app = Flask(__name__)

@app.route('/args', methods=['GET'])
def get_args():
    return app.send_static_file('sample_args.json')

@app.route('/args', methods=['POST'])
def post_args():
    args = request.json
    
    args['hospitalized'] = RateLos(args['hospitalized_rate'], args['hospitalized_los'])
    args['icu'] = RateLos(args['icu_rate'], args['icu_los'])
    args['ventilated'] = RateLos(args['ventilated_rate'], args['ventilated_los'])

    del args['hospitalized_rate']
    del args['hospitalized_los']
    del args['icu_rate']
    del args['icu_los']
    del args['ventilated_rate']
    del args['ventilated_los']
    
    p = Parameters(**args)
    m = SimSirModel(p)

    files = []
    prefix = datetime.now().strftime("%Y.%m.%d.%H.%M.")
    for df, name in (
        (m.raw_df, "raw"),
        (m.admits_df, "admits"),
        (m.census_df, "census"),
    ):
        filename = path.join(gettempdir(), prefix + name + ".csv")
        df.to_csv(filename)
        files.append(filename)

    zipfilename = path.join(gettempdir(), prefix + 'result.zip')
    with ZipFile(zipfilename, 'w') as zip:
        for file in files:
            zip.write(file, path.basename(file))
    return send_file(zipfilename)
