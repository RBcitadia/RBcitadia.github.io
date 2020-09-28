from flask import Blueprint, request, jsonify, url_for, g
import tkinter as tk
from tkinter.filedialog import askdirectory, askopenfilename
import os
import geopandas as gpd
import pandas as pd
import json
from time import process_time, strftime, localtime
from . source import explode, clean_data, tryOverlay, coeffEmpriseSol, selectionParcelles, test_emprise_vide, test_emprise_batie, routeCadastrees, voiesFerrees, filtre

bp = Blueprint('potentiel', __name__)

@bp.route("/import_donnees", methods=['POST'])
def import_donnees():
    data = request.form.to_dict(flat=False)
    g.couches = {}
    for k in data:
        if k == 'Structuration territoriale':
            if '*' in data[k][0]:
                nom = (data[k][0].split('*'))
                g.couches[k] = clean_data(gpd.read_file(nom[0], layer=nom[1], driver='GPKG'), keep=False)
            else:
                g.couches[k] = clean_data(gpd.read_file(data[k][0]), keep=False)
        elif '*' in data[k][0] and k != 'Structuration territoriale':
            print("It's a Geopackage layer")
            nom = (data[k][0].split('*'))
            g.couches[k] = clean_data(gpd.read_file(nom[0], layer=nom[1], driver='GPKG'))
        else:
            print("It's a shape layer!")
            g.couches[k] = clean_data(gpd.read_file(data[k][0]))
    structure = g.couches['Structuration territoriale']
    for i in structure.columns:
        if structure[i].dtypes == 'object':
            structure[i].fillna('Valeur nulle', inplace = True)
        else:
            structure[i].fillna(0, inplace = True)
    liste = [i for i in structure.columns]
    # structure.insert(len(structure.columns), "d_min_route", 100)
    structure.crs = "EPSG:2154"
    structure.insert(len(structure.columns), "non-batie", 400)
    structure.insert(len(structure.columns), "batie", 1000)
    structure.insert(len(structure.columns), "cesMax", 40)
    structure.insert(len(structure.columns), "test", 10)
    structure.insert(len(structure.columns), "bufBati", 4)
    print(liste)
    return jsonify(liste)

@bp.route("/lancement", methods=['POST'])
def lancement():
    print(g.structure)
    print(g.enveloppe)
    # data = request.form.to_dict(flat=False)
    # print(data)
    # for item in data.items():
    #     donnees = json.loads(item[0])
    # print(donnees)
    # print(type(donnees))
    # t0 = process_time()
    # def timing(t, intitule):
    #     temps = process_time() - t
    #     if temps <=60:
    #         unite = 'secondes'
    #         temps = round(temps, 1)
    #     else:
    #         temps = round(temps / 60, 1)
    #         unite = 'minutes'
    #     print("\n   #####   {} {} {}  #####   \n".format(intitule,temps,unite))
    # print('\n   ##### Lancement du traitement #####   \n'+ '\n' + strftime("%a, %d %b %Y %H:%M:%S", localtime())+ '\n' + '\n   ##   Prise en compte de la structuration territoriale   ##   \n')
    # #eel.progress(90/7)
    # if "Structuration territoriale" in donnees["dossier"]["couches"] or "Structuration territoriale" in donnees["gpkg"]["layers"]:
    #     if donnees['paramètres']['perso'] == 'vide':
    #         param = donnees["paramètres"]["défauts"]
    #         global enveloppe
    #         enveloppe = clean_data(structure, ["non-batie", "batie", "cesMax", "test", "bufBati"])
    #         enveloppe["geometry"] = enveloppe.buffer(0)
    #         # enveloppe['d_min_route'] = param['d_min_route']
    #         enveloppe['non-batie'] = int(param['non-batie'])
    #         enveloppe['batie'] = int(param['batie'])
    #         enveloppe['cesMax'] = int(param['cesMax'])
    #         enveloppe['test'] = int(param['test'])
    #         enveloppe['bufBati'] = int(param['bufBati'])
    #     else:
    #         param = donnees["paramètres"]["perso"]["valeurs"]
    #         liste = list(param.keys()) # nom des lignes
    #         champs = donnees["paramètres"]["perso"]["champs"]
    #         # l_route = [item["d_min_route"] for item in param.values()]
    #         l_non_batie = [item["non-batie"] for item in param.values()]
    #         l_batie = [item["batie"] for item in param.values()]
    #         l_ces = [item["cesMax"] for item in param.values()]
    #         l_test = [item["test"] for item in param.values()]
    #         l_buf_bati = [item["bufBati"] for item in param.values()]
    #         d = {
    #             champs : liste,
    #             # "d_min_route" : l_route,
    #             "non-batie" : l_non_batie,
    #             "batie" : l_batie,
    #             "cesMax" : l_ces,
    #             "test" : l_test,
    #             "bufBati" : l_buf_bati
    #         }
    #         df = pd.DataFrame(d)
    #         df = df.set_index(champs)
    #         enveloppe.update(df,overwrite=True)
    #
    # #Récupération des couches sélectionnées dans l'interface
    # print("\n   ##   Récupération des couches   ##   \n")
    # couches = ["Parcelles", "Bâti", "Routes", "Voies ferrées"]
    # chemins = {}
    # for couche in couches:
    #     print(f"\n   - Récupération de la couche {couche}")
    #     ti = process_time()
    #     if couche in donnees["dossier"]["couches"]:
    #         chemins[couche] = clean_data(gpd.read_file(donnees["dossier"]["chemin"] + '/' + donnees["dossier"]["couches"][couche]))
    #     elif couche in donnees["gpkg"]["layers"]:
    #         chemins[couche] = clean_data(gpd.read_file(donnees["gpkg"]["nomGPKG"], layer=donnees["gpkg"]["layers"][couche]))
    #     timing(ti, f'{couche} récupéré en')
    # #Selection des parcelles qui touchent l'enveloppe
    # parcelle = chemins["Parcelles"]
    # try:
    #     parcelle_intersect = gpd.overlay(parcelle, enveloppe, how='intersection')
    #     parcelle_intersect.crs = enveloppe.crs
    # except NameError:
    #     param = donnees["paramètres"]["défauts"]
    #     parcelle['non-batie'] = int(param['non-batie'])
    #     parcelle['batie'] = int(param['batie'])
    #     parcelle['cesMax'] = int(param['cesMax'])
    #     parcelle['test'] = int(param['test'])
    #     parcelle['bufBati'] = int(param['bufBati'])
    #
    # timing(ti, 'Prise en compte de la structuration territoriale terminée en')
    # #Calcul du CES
    # #eel.progress(90/7)
    # ti = process_time()
    # global ces
    # try:
    #     ces = coeffEmpriseSol(chemins["Bâti"], parcelle_intersect)
    # except UnboundLocalError:
    #     ces = coeffEmpriseSol(chemins["Bâti"], parcelle)
    # timing(ti, 'Calcul du CES terminé en')
    # #Sélection des parcelles
    # #eel.progress(90/7)
    # ti = process_time()
    # selection = selectionParcelles(ces)
    # selection_initiale = selection.copy()
    # timing(ti, 'Sélection des parcelles terminé en')
    # global exclues
    # #Prise en compte des routes cadastrées
    # if "Routes" in chemins:
    #     #eel.progress(90/7)
    #     ti = process_time()
    #     route = chemins["Routes"]
    #     try:
    #         routes_in_enveloppe = gpd.overlay(route, enveloppe, how='intersection')
    #         routes_in_enveloppe = routes_in_enveloppe[routes_in_enveloppe.geometry.notnull()]
    #         selection1, exclues = routeCadastrees(routes_in_enveloppe, selection)
    #         timing(ti, 'Exclusion des routes cadastrées terminée en')
    #     except NameError:
    #         selection1, exclues = routeCadastrees(route, selection)
    #         timing(ti, 'Exclusion des routes cadastrées terminée en')
    #     except IndexError:
    #         print("MESSAGE : Les routes n'intersectent pas les parcelles!")
    #         chemins.pop("Routes")
    #     #potentiel = routeDesserte(routes_in_enveloppe, potentiel)
    #     #timing(ti, 'Prise en compte de la proximité à la route terminée en')
    #     #ti = process_time()
    #
    # else:
    #     pass
    #     #eel.progress(90/7)
    # #Prise en compte des voies ferrées si renseignées
    # if "Voies ferrées" in chemins:
    #     #eel.progress(90/7)
    #     if "Routes" in chemins:
    #         try:
    #             selection, exclues = voiesFerrees(chemins["Voies ferrées"], selection1, exclues)
    #         except NameError:
    #             selection, exclues = voiesFerrees(chemins["Voies ferrées"], selection1)
    #     else:
    #         try:
    #             selection, exclues = voiesFerrees(chemins["Voies ferrées"], selection, exclues)
    #         except NameError:
    #             selection, exclues = voiesFerrees(chemins["Voies ferrées"], selection)
    # else:
    #     pass
    #     #eel.progress(90/7)
    # #Prise en compte des Filtres
    # #eel.progress(90/7)
    # for couche in donnees["dossier"]["couches"]:
    #     if couche not in couches and couche != 'Structuration territoriale':
    #         chemins[couche] = clean_data(gpd.read_file(donnees["dossier"]["chemin"] + '/' + donnees["dossier"]["couches"][couche]))
    #         try:
    #             selection, exclues = filtre(selection, chemins[couche], int(donnees["paramètres"]["filtres"][couche]), couche, exclues)
    #         except NameError:
    #             selection, exclues = filtre(selection, chemins[couche], int(donnees["paramètres"]["filtres"][couche]), couche)
    # for couche in donnees["gpkg"]["layers"]:
    #     if couche not in couches and couche != 'Structuration territoriale':
    #         chemins[couche] = clean_data(gpd.read_file(donnees["gpkg"]["nomGPKG"], layer=donnees["gpkg"]["layers"][couche]))
    #         try:
    #             selection, exclues = filtre(selection, chemins[couche], int(donnees["paramètres"]["filtres"][couche]), couche, exclues)
    #         except NameError:
    #             selection, exclues = filtre(selection, chemins[couche], int(donnees["paramètres"]["filtres"][couche]), couche)
    # #Test des parcelles vides identifiées
    # #eel.progress(90/7)
    # ti = process_time()
    # parcelle_vide = selection[selection["Potentiel"] == "Dents creuses"]
    # try:
    #     emprise_vide, exclues = test_emprise_vide(parcelle_vide, exclues)
    # except NameError:
    #     emprise_vide = test_emprise_vide(parcelle_vide)
    # #Test des parcelles baties identifiées
    # parcelle_batie = selection[selection["Potentiel"] == "Division parcellaire"]
    # global boundingBox
    # try:
    #     emprise_batie, boundingBox, exclues = test_emprise_batie(parcelle_batie, chemins["Bâti"], exclues)
    # except NameError:
    #     emprise_batie, boundingBox = test_emprise_batie(parcelle_batie, chemins["Bâti"])
    # timing(ti, 'Test des parcelles terminé en')
    # global potentiel_emprise
    # parcelle_vide = parcelle_vide.loc[parcelle_vide['id_par'].isin(i for i in emprise_vide['id_par'])]
    # liste_id_vide = [ i for i in emprise_vide['id_par']]
    # potentiel_emprise = pd.concat([emprise_batie, selection_initiale.loc[selection_initiale['id_par'].isin(set(liste_id_vide))]])
    # potentiel_emprise = explode(potentiel_emprise)
    # boundingBox = pd.concat([boundingBox, parcelle_vide])
    # boundingBox.reset_index(inplace=True)
    # boundingBox.loc[boundingBox['id_par'].isnull(), "id_par"] = boundingBox["id_par_1"]
    # boundingBox = boundingBox[boundingBox["geometry"].is_valid]
    # boundingBox = boundingBox[boundingBox["geometry"].notnull()]
    # #boundingBox["Surf"] = round(boundingBox.geometry.area, 2)
    # boundingBox.drop("id_par_1", axis=1)
    # global potentiel
    # liste_id = [i for i in emprise_vide["id_par"]] + [i for i in boundingBox["id_par_1"]]
    # potentiel = selection_initiale.loc[selection_initiale['id_par'].isin(set(liste_id))]
    # try:
    #     exclues = exclues.loc[~exclues['id_par'].isin(set(liste_id + [i for i in emprise_batie["id_par"]]))]
    #     exclues.loc[exclues.geometry.isna(), "test_emprise"]
    # except NameError:
    #     pass
    #
    # def ajout_champs(couche):
    #     couche.insert(len(couche.columns), "Surf",round(couche.geometry.area, 2))
    #     try:
    #         couche.insert(len(couche.columns), "Commune",'')
    #     except ValueError:
    #         couche.insert(len(couche.columns), "Commune1",'')
    #     try:
    #         couche.insert(len(couche.columns), "Comment",'')
    #     except ValueError:
    #         couche.insert(len(couche.columns), "Comment1",'')
    #     couche.insert(len(couche.columns), "Date",strftime("%d-%m-%Y", localtime()))
    #     couche.insert(len(couche.columns), "Suppr",'')
    #
    # ajout_champs(potentiel)
    # ajout_champs(potentiel_emprise)
    # ajout_champs(boundingBox)
    # try:
    #     ajout_champs(exclues)
    # except NameError:
    #     pass
    # timing(t0, 'Traitement terminé! en')
    # print('\n' + strftime("%a, %d %b %Y %H:%M:%S", localtime()))
    # return "Traitement terminé!!"
