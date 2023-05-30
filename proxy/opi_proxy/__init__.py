#!/usr/bin/python3

import os
import json

import requests
from flask import Flask, request, Response

app = Flask(__name__)

CONFIG_FILE = os.environ.get('CONFIG', 'config.json')
config = json.load(open(CONFIG_FILE))

@app.route('/')
def endpoint():
	c = config[request.args['obs_instance']]
	assert request.args['obs_api_link'].startswith(c['url'])
	r = requests.get(request.args['obs_api_link'], auth=(c['user'], c['pass']))
	r.raise_for_status()
	return Response(
		r.text,
		status=r.status_code,
		headers={
			'Access-Control-Allow-Origin': '*'
		},
		mimetype=r.headers.get('content-type', 'text/plain')
	)

if __name__ == '__main__':
	app.run(host='0.0.0.0', debug=True)
