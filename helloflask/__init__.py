from flask import Flask

app = Flask(__name__)

app.secret_key = 'helloflask'

import helloflask.views
import helloflask.openid_views
