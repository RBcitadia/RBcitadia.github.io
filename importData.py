from flask import Blueprint, request, jsonify, url_for, g
import tkinter as tk
from tkinter.filedialog import askdirectory, askopenfilename
import os
import geopandas as gpd
import pandas as pd
import json
from time import process_time, strftime, localtime
from fiona import listlayers
from . source import clean_data


bp = Blueprint('importData', __name__)

@bp.route('/selectionDossier')
def selectionDossier():
    root = tk.Tk()
    global choix_du_dossier
    choix_du_dossier = askdirectory()
    #root.withdraw()
    root.destroy()
    return choix_du_dossier

@bp.route('/selectionBDgpkg')
def selectionBDgpkg():
    root = tk.Tk()
    global choix_du_dossier
    choix_du_dossier = askopenfilename(title="Sélectionner la Base de donnée", filetypes=[("geopackage files", "*.gpkg")])
    #root.withdraw()
    root.destroy()
    return choix_du_dossier

@bp.route("/liste_data", methods=['POST'])
def liste_data():
    donnee = []
    data = request.form.to_dict(flat=False)
    chemin = data['chemin'][0]
    if chemin.endswith('.gpkg'):
        for layerName in listlayers(chemin):
            donnee.append(layerName)
    else:
        for root, dirs, files in os.walk(chemin):
            for item in files:
                if item.endswith('.shp') or item.endswith('.geojson'):
                    donnee.append(item)
    return jsonify(donnee)

@bp.route("/geometryType", methods=['POST'])
def geometryType():
    data = request.form.to_dict(flat=False)
    chemin = data['chemin'][0]
    nom = data['layer'][0]
    try:
        if chemin.endswith('gpkg'):
            couche = gpd.read_file(chemin, layer=nom)
        else:
            couche = gpd.read_file(chemin + '/' + nom)
        if len(couche) == 0:
            return "Couche vide"
    except UnicodeDecodeError:
        print("MESSAGE : Ne soyez pas comme Bruno, ne mettez pas d'accents dans le nom de vos champs! ;) ")
    else:
        type = str(couche["geometry"][0].geom_type)
        return type

@bp.route("/unique_values", methods=['POST'])
def unique_values():
    data = request.form.to_dict(flat=False)
    champs = data['champs'][0]
    try:
        structure = gpd.read_file(data['couche'][0])
    except KeyError:
        structure = gpd.read_file(data['couche[]'][0], layer = data['couche[]'][1])
    structure = structure.dissolve(by=champs).reset_index()
    liste_valeur = list(structure[champs])
    print(liste_valeur)
    return jsonify(liste_valeur)
