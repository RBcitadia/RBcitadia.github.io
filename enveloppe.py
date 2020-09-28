import geopandas as gpd
import pandas as pd
from flask import Blueprint, request, jsonify, url_for

bp = Blueprint('enveloppe', __name__)

## Erosion-Dilatation : définition de l'enveloppe Brut
@bp.route('/', methods=['POST'])
def enveloppe():
    ## Récupération de la donnée
    # Données : donnees, surf_bati_min, dilatation, erosion, bufbati_env
    couches = ["Parcelles", "Bâti", "Routes", "Voies ferrées"]
    chemins = {}
    dossier = donnees["dossier"]["chemin"]
    for couche in couches:
        print(f"\n   - Récupération de la couche {couche}")
        ti = process_time()
        if couche in donnees["dossier"]["couches"]:
            chemins[couche] = clean_data(gpd.read_file(donnees["dossier"]["chemin"] + '/' + donnees["dossier"]["couches"][couche]))
        elif couche in donnees["gpkg"]["layers"]:
            chemins[couche] = clean_data(gpd.read_file(donnees["gpkg"]["nomGPKG"], layer=donnees["gpkg"]["layers"][couche]))
    for couche in donnees["dossier"]["couches"]:
        if couche not in couches:
            chemins[couche] = clean_data(gpd.read_file(donnees["dossier"]["chemin"] + '/' + donnees["dossier"]["couches"][couche]))
    for couche in donnees["gpkg"]["layers"]:
        if couche not in couches:
            chemins[couche] = clean_data(gpd.read_file(donnees["gpkg"]["nomGPKG"], layer=donnees["gpkg"]["layers"][couche]))
    #extraction du bati dont la superficie est superieure à [seuil utilisateur]
    print("\n 1 - Erosion-Dilatation : définition de l'enveloppe Brut\n")
    bati = chemins['Bâti']
    bati = clean_data(bati)
    surf_bati_min = int(surf_bati_min)
    bati_tri = bati[bati.geometry.area >= surf_bati_min]
    bati_dilatation = bati_tri.copy()
    dilatation = int(dilatation)
    bati_dilatation.geometry = bati_dilatation.buffer(dilatation)
    bati_dilatation.insert(1,"diss",1)
    dissolve = bati_dilatation.dissolve("diss", as_index=False)
    erosion = int(erosion)
    bati_erosion = dissolve.copy()
    bati_erosion.geometry = dissolve.buffer(erosion)
    enveloppe_brut = clean_data(bati_erosion)
    enveloppe_brut.to_file(dossier + '/enveloppe.gpkg', layer='1_enveloppe_brut', driver='GPKG')
    print("Couche '1_envelope_brut' exportée!")

    print("\n 2 - Dissoudre le buffer +50-30 du bati avec : terrains de sport, surfaces d'activités et cimetières (BD topo)\n")
    dissolution = enveloppe_brut.copy()
    for couche in chemins.keys():
        if couche not in couches:
            dissolution = pd.concat([dissolution, chemins[couche]])
    dissolution.reset_index(inplace=True)
    dissolution.insert(len(dissolution.columns), "commun", "1")
    dissolution = dissolution.dissolve(by='commun').reset_index()
    dissolution = clean_data(dissolution)
    dissolution.to_file(dossier + '/enveloppe.gpkg', layer='2_dissolution', driver='GPKG')
    print("Couche '2_dissolution' exportée!")

    print("\n 3 - Emprise de l'enveloppe par rapport à la parcelle\n")
    parcelle_enveloppe = chemins["Parcelles"].copy()
    parcelle_enveloppe.insert(0,"id_par",range(1,1+len(parcelle_enveloppe)))
    parcelle_enveloppe.insert(len(parcelle_enveloppe.columns), "surf_par", parcelle_enveloppe.geometry.area)
    intersection = gpd.overlay(parcelle_enveloppe, dissolution, how='intersection')
    intersection.insert(len(intersection.columns), "surf_env", intersection.geometry.area)
    liste_par_env = [i for i in intersection["id_par"]]
    parcelles_entieres = parcelle_enveloppe.loc[parcelle_enveloppe["id_par"].isin(liste_par_env)]
    parcelles_entieres.to_file(dossier + '/enveloppe.gpkg', layer='3_parcelles_entieres', driver='GPKG')
    print("Couche '3_parcelles_entieres' exportée!")

    print("\n 4 - Seuil fort/faible")
    intersection["emprise"] = intersection["surf_env"] / intersection["surf_par"] *100
    faible = intersection[intersection["emprise"] <= 50]
    liste_faible = [i for i in faible["id_par"]]
    emprise_faible = parcelle_enveloppe.loc[parcelle_enveloppe["id_par"].isin(liste_faible)]
    emprise_faible.to_file(dossier + '/enveloppe.gpkg', layer='4_emprise_faible', driver='GPKG')
    print("Couche '4_emprise_faible' exportée!")
    forte = intersection[intersection["emprise"] > 50]
    liste_forte = [i for i in intersection["id_par"]]
    emprise_forte = parcelle_enveloppe.loc[parcelle_enveloppe["id_par"].isin(liste_forte)]
    emprise_forte.to_file(dossier + '/enveloppe.gpkg', layer='4_emprise_forte', driver='GPKG')
    print("Couche '4_emprise_forte' exportée!")

    print("\n 5 - Intersection emprise faible et buffer autour du bâti")
    bati_buffer = chemins["Bâti"].copy()
    bufbati_env = int(bufbati_env)
    bati_buffer.geometry = bati_buffer.buffer(bufbati_env)
    bati_buffer = clean_data(bati_buffer)
    intersection2 = gpd.overlay(emprise_faible,bati_buffer, how='intersection')
    intersection2.insert(1, "id_bat", range(1,1+len(intersection2)))
    intersection2.to_file(dossier + '/enveloppe.gpkg', layer='5_empriseFaible_batiBuf', driver='GPKG')
    print("Couche '5_empriseFaible_batiBuf' exportée!")
