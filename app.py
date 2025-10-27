from flask import Flask, render_template, redirect, url_for, request, flash
import os
from dotenv import load_dotenv

# Importez vos fonctions depuis vos fichiers séparés
from download_and_save_inventory import download_inventory_file
from download_and_save_catalog_details import download_and_save_catalog_files
from get_folder_info import get_folder_content

# Charger les variables d'environnement
load_dotenv()

app = Flask(__name__)
# Une clé secrète est requise pour utiliser les messages flash
app.secret_key = os.getenv("FLASK_SECRET_KEY", "une-cle-secrete-par-defaut")

@app.route('/')
def index():
    inventory_files = get_folder_content("INVENTAIRE-PARTS-CANADA")
    
    # Listez ici tous les catalogues que vous voulez gérer
    # Pour en ajouter un, il suffit d'ajouter son nom à cette liste
    managed_catalogs = ["snow", "fatbook", "street", "atv-utv", "offroad", "tire-and-service"]
    
    # Récupère les informations pour chaque dossier de catalogue
    catalog_files_data = {
        name: get_folder_content(f"CATALOGUES-{name}") for name in managed_catalogs
    }
        
    return render_template('index.html', 
                           inventory_files=inventory_files, 
                           catalog_data=catalog_files_data)

@app.route('/lancer-telechargement-inventaire', methods=['POST'])
def lancer_telechargement_inventaire():
    try:
        download_inventory_file(endpoint="/inventory")
        flash("Téléchargement de l'inventaire réussi.", "success")
    except Exception as e:
        flash(f"Une erreur est survenue lors du téléchargement de l'inventaire : {e}", "error")
    return redirect(url_for('index'))

# --- NOUVELLE ROUTE DYNAMIQUE ---
@app.route('/lancer-telechargement-catalogue/<string:catalog_name>', methods=['POST'])
def lancer_telechargement_catalogue(catalog_name):
    """
    Route dynamique pour télécharger n'importe quel catalogue spécifié.
    """
    try:
        download_and_save_catalog_files(catalog_name=catalog_name)
        flash(f"Téléchargement du catalogue '{catalog_name}' réussi.", "success")
    except Exception as e:
        flash(f"Erreur lors du téléchargement du catalogue '{catalog_name}': {e}", "error")
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)

