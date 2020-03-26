from collections import namedtuple
from datetime import datetime
from os import path
from tempfile import gettempdir
from zipfile import ZipFile

from flask import Flask, request, send_file

from penn_chime.models import SimSirModel
from penn_chime.parameters import Parameters
from penn_chime.utils import RateLos

application = Flask(__name__)

@application.route('/api/readme', methods=['GET'])
def get_readme():
    return """
# Chime API

This API wraps the modeling engine that backs the [COVID-19 Hospital Impact Model for Epidemics tool](https://codeforphilly.github.io/chime/)

## Usage

When following these instructions replace <host> with the actual host. Currently this is "dry-basin-64387.herokuapp.com".

To see these instructions: `curl https://<host>/api/readme`

To retrieve a JSON file that contains the required arguments:

`curl https://<host>/api/args > args.json`

Modify the args file with your parameters, then post the file to the API:

`curl -X POST -d @args.json -H "content-type: application/json"  https://<host>/api/args --output results.zip && unzip results.zip`

Note that this is a quick and dirty wrapper and should not be thought of as production-quality code. For example, no validation is done on inputs. If you get a server error when POSTing some parameters, make a change and try again.
"""

@application.route('/api/args', methods=['GET'])
def get_args():
    return application.send_static_file('sample_args.json')

@application.route('/api/args', methods=['POST'])
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
