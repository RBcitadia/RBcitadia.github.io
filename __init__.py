import os
from flask import Flask, render_template
from . import importData, potentiel, enveloppe
from dotenv import load_dotenv

#load dotenv in the base root
APP_ROOT = os.path.join(os.path.dirname(__file__), '..') # refers to application_top
dotenv_path = os.path.join(APP_ROOT, '.env')
load_dotenv(dotenv_path)

app = Flask(__name__)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
app.register_blueprint(potentiel.bp, url_prefix='/potentiel')
app.register_blueprint(importData.bp, url_prefix='/importData')
app.register_blueprint(enveloppe.bp, url_prefix='/enveloppe')

@app.route('/')
def home():
    return render_template('index.html')
