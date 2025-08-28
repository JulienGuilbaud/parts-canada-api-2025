# Nom du fichier : app.py
# Pour l'exécuter :
# 1. Créez un dossier "templates" et placez "index.html" à l'intérieur.
# 2. Lancez ce serveur : python app.py
# 3. Ouvrez votre navigateur et allez à l'adresse http://127.0.0.1:5000

from flask import Flask, jsonify, render_template
from flask_cors import CORS
import os
import webbrowser
from threading import Timer

# Importez la logique de votre script existant.
from download_and_save_inventory import download_inventory_file

app = Flask(__name__)
CORS(app)

# --- Routes de l'API ---

@app.route('/')
def index():
    """
    Sert la page principale de l'application (index.html).
    """
    return render_template('index.html')

@app.route('/download/inventory', methods=['GET'])
def handle_inventory_download():
    """
    Endpoint pour télécharger le fichier d'inventaire principal.
    """
    try:
        # Appelle la fonction importée de votre script
        output_path = download_inventory_file(
            endpoint="/inventory", 
            zip_filename="inventory.zip", 
            csv_filename="inventory.csv"
        )
        return jsonify({"message": f"Fichier d'inventaire sauvegardé dans : {output_path}"}), 200
    except Exception as e:
        # Log l'erreur côté serveur pour le débogage
        print(f"Erreur lors du téléchargement de l'inventaire : {e}")
        # Renvoie une réponse d'erreur claire au frontend
        return jsonify({"error": str(e)}), 500

def open_browser():
    """
    Ouvre le navigateur web à la bonne adresse après le démarrage du serveur.
    """
    webbrowser.open_new('http://127.0.0.1:5000/')

# --- Point d'entrée du serveur ---
if __name__ == '__main__':
 
    
    # Lance le serveur en mode débogage, accessible sur votre machine locale
    app.run(debug=True, port=5000)
