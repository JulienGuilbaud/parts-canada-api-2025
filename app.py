from flask import Flask, render_template, redirect, url_for
from download_and_save_inventory import download_inventory_file
import os
import datetime

# Initialisation de l'application Flask
app = Flask(__name__)

# Route principale qui affiche la page web
@app.route('/')
def index():
    target_folder = "INVENTAIRE-PARTS-CANADA"
    file_properties = []

    # Vérifier si le dossier cible existe
    if os.path.exists(target_folder):
        # Lister tous les fichiers dans le dossier
        for filename in os.listdir(target_folder):
            file_path = os.path.join(target_folder, filename)
            # S'assurer que c'est bien un fichier
            if os.path.isfile(file_path):
                try:
                    # Obtenir les statistiques du fichier
                    stats = os.stat(file_path)
                    # Formater la date de modification pour une lecture facile
                    mod_time = datetime.datetime.fromtimestamp(stats.st_mtime).strftime('%Y-%m-%d %H:%M:%S')
                    # Calculer la taille en Mo
                    size_mo = round(stats.st_size / (1024 * 1024), 2)
                    
                    file_properties.append({
                        'name': filename,
                        'mod_date': mod_time,
                        'size_mo': size_mo
                    })
                except Exception as e:
                    print(f"Impossible de lire les propriétés de {filename}: {e}")

    # On passe la liste des fichiers et leurs propriétés au template
    return render_template('index.html', files=file_properties)

# Route qui est appelée lorsque l'on clique sur le bouton
@app.route('/lancer-telechargement', methods=['POST'])
def lancer_telechargement():
    try:
        download_inventory_file(endpoint="/inventory")
    except Exception as e:
        print(f"Une erreur est survenue lors du téléchargement : {e}")
        # Même en cas d'erreur, on redirige. L'utilisateur verra que la liste
        # des fichiers n'a pas changé, ce qui indique un problème.
        # L'erreur est visible dans la console du serveur.
    
    # On redirige vers la page d'accueil pour rafraîchir la liste des fichiers
    return redirect(url_for('index'))

# Point d'entrée pour lancer le serveur web
if __name__ == '__main__':
    app.run(debug=True)

