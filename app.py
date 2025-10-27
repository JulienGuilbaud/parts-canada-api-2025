from flask import Flask, render_template, redirect, url_for, request
import os # Importation de OS
from download_and_save_inventory import download_inventory_file
from download_and_save_catalog_details import download_and_save_catalog_files
from get_folder_info import get_folder_content
from download_commodity_codes import download_commodity_codes_file
from transform_commodity import transformer_codes_commodite
from download_extended_inventory import download_extended_inventory_file
# --- L'importation de 'download_product_features' est SUPPRIMÉE ---

app = Flask(__name__)

# --- CONFIGURATION DE LA LISTE DES CATALOGUES ---
CATALOGUES_A_GERER = [
    "snow",
    "fatbook",
    "street",
    "atv-utv",
    "offroad",
    "helmet-and-apparel",
    "bicycle",
    "tire-and-service",
    "oldbook"
]
# ------------------------------------------------

@app.route('/')
def index():
    """
    Affiche la page d'accueil avec l'état des dossiers.
    """
    inventory_files = get_folder_content("INVENTAIRE-PARTS-CANADA")
    commodity_files = get_folder_content("COMMODITY-CODES")
    extended_inventory_files = get_folder_content("INVENTAIRE-ETENDU-PARTS-CANADA")
    
    # Récupérer les infos pour tous les catalogues gérés
    catalog_data = {}
    for catalog_name in CATALOGUES_A_GERER:
        folder_name = f"CATALOGUES-{catalog_name}"
        # Définir le chemin du sous-dossier pour les features
        features_folder_name = os.path.join(folder_name, "FEATURES")

        catalog_data[catalog_name] = {
            'name': catalog_name,
            'folder_name': folder_name,
            'files': get_folder_content(folder_name),
            'features_folder_name': features_folder_name,
            'features_files': get_folder_content(features_folder_name)
        }

    return render_template(
        'index.html', 
        inventory_files=inventory_files,
        commodity_files=commodity_files,
        extended_inventory_files=extended_inventory_files,
        catalog_data=catalog_data
    )

@app.route('/lancer-telechargement-inventaire', methods=['POST'])
def lancer_telechargement_inventaire():
    """
    Route pour démarrer le téléchargement de l'inventaire.
    """
    try:
        download_inventory_file(endpoint="/inventory")
    except Exception as e:
        print(f"Une erreur est survenue lors du téléchargement de l'inventaire : {e}")
    return redirect(url_for('index'))

@app.route('/lancer-telechargement-inventaire-etendu', methods=['POST'])
def lancer_telechargement_inventaire_etendu():
    """
    Route pour démarrer le téléchargement de l'inventaire étendu.
    """
    try:
        download_extended_inventory_file()
    except Exception as e:
        print(f"Une erreur est survenue lors du téléchargement de l'inventaire étendu : {e}")
    return redirect(url_for('index'))

@app.route('/lancer-telechargement-commodity', methods=['POST'])
def lancer_telechargement_commodity():
    """
    Route pour démarrer le téléchargement des codes de commodité.
    """
    try:
        download_commodity_codes_file()
    except Exception as e:
        print(f"Une erreur est survenue lors du téléchargement des codes de commodité : {e}")
    return redirect(url_for('index'))

@app.route('/lancer-telechargement-catalogue/<string:catalog_name>', methods=['POST'])
def lancer_telechargement_catalogue(catalog_name):
    """
    Route dynamique pour démarrer le téléchargement d'un catalogue.
    """
    if catalog_name not in CATALOGUES_A_GERER:
        print(f"Erreur : Tentative de téléchargement pour un catalogue non géré : {catalog_name}")
        return redirect(url_for('index'))
    
    try:
        download_and_save_catalog_files(catalog_name=catalog_name)
    except Exception as e:
        print(f"Une erreur est survenue lors du téléchargement du catalogue '{catalog_name}': {e}")
    return redirect(url_for('index'))

# --- La route '/lancer-telechargement-features' a été SUPPRIMÉE ---


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)

