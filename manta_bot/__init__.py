from __future__ import unicode_literals
import os
import json
from flask import Flask
from flask import request
from .manta_bot import Manta


app = Flask(__name__, instance_relative_config=False)

# App configuration
home_dir = os.path.expanduser('~')
config_path = os.path.join(home_dir, '.config/manta/config.py')

if os.path.isfile(config_path):
    app.config.from_pyfile(config_path)

API_TOKEN = app.config.get('API_TOKEN', '')
WEBHOOK = app.config.get('WEBHOOK', '')


bot = Manta(API_TOKEN, WEBHOOK)


@app.route("/"+API_TOKEN, methods=['POST'])
def hook():
    update = json.loads(request.data.decode('utf-8'))
    bot.handle_update(update)
    return 'OK'

