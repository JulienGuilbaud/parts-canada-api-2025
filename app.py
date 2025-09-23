from flask import Flask, render_template, redirect, url_for, request
from download_and_save_inventory import download_inventory_file
from download_and_save_catalog_details import download_and_save_catalog_files
from get_folder_info import get_folder_content


app = Flask(__name__)


@app.route('/')
def index():
    inventory_files = get_folder_content("INVENTAIRE-PARTS-CANADA")
    catalog_files = get_folder_content("CATALOGUES-snow")
    return render_template('index.html', inventory_files=inventory_files, catalog_files=catalog_files)

@app.route('/lancer-telechargement-inventaire', methods=['POST'])
def lancer_telechargement_inventaire():
    try:
        download_inventory_file(endpoint="/inventory")
    except Exception as e:
        print(f"Une erreur est survenue lors du téléchargement de l'inventaire : {e}")
    return redirect(url_for('index'))

@app.route('/lancer-telechargement-catalogue-snow', methods=['POST'])
def lancer_telechargement_catalogue_snow():
    try:
        download_and_save_catalog_files(catalog_name="snow")
    except Exception as e:
        print(f"Une erreur est survenue lors du téléchargement du catalogue snow': {e}")
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)

