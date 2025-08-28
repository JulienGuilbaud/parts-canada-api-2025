# Nom du fichier : download_and_save_inventory.py
# (Version modifiée pour être importable)

import requests
import os
import zipfile
from dotenv import load_dotenv

# --- Configuration ---
load_dotenv()
API_KEY = os.environ.get('PARTS_CANADA_API_KEY')
BASE_URL = "https://sandbox-api.partscanada.com/api/v2"
OUTPUT_DIR = "source"

def print_colored(text, color):
    """Affiche du texte en couleur dans le terminal."""
    colors = {
        "header": "\033[95m", "blue": "\033[94m", "green": "\033[92m",
        "warning": "\033[93m", "fail": "\033[91m", "endc": "\033[0m", "bold": "\033[1m"
    }
    print(f"{colors.get(color, '')}{text}{colors['endc']}")

def download_inventory_file(endpoint, zip_filename, csv_filename):
    """
    Fonction générique pour télécharger, décompresser et enregistrer un fichier
    depuis l'API de Parts Canada.
    Retourne le chemin du fichier CSV final.
    """
    print_colored(f"--- Lancement du téléchargement pour l'endpoint : {endpoint} ---", "header")

    if not API_KEY:
        raise ValueError("La clé d'API (PARTS_CANADA_API_KEY) n'est pas définie.")

    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        print_colored(f"  - Dossier '{OUTPUT_DIR}' créé.", "green")

    url = f"{BASE_URL}{endpoint}"
    headers = {'Authorization': f'Bearer {API_KEY}'}
    zip_path = os.path.join(OUTPUT_DIR, zip_filename)
    output_path = os.path.join(OUTPUT_DIR, csv_filename)

    try:
        print_colored(f"> Appel de l'API : {url}", "blue")
        response = requests.get(url, headers=headers, timeout=120, stream=True)
        response.raise_for_status()
        
        with open(zip_path, 'wb') as f:
            f.write(response.content)
        print_colored(f"  - Fichier ZIP sauvegardé dans : {zip_path}", "green")

        print_colored(f"> Décompression de {zip_path}...", "blue")
        with zipfile.ZipFile(zip_path, 'r') as z:
            csv_internal_path = next((name for name in z.namelist() if name.lower().endswith('.csv')), None)
            
            if not csv_internal_path:
                raise FileNotFoundError("Aucun fichier CSV trouvé dans l'archive ZIP.")

            print_colored(f"  - Fichier CSV trouvé dans l'archive : {csv_internal_path}", "green")
            
            with z.open(csv_internal_path) as source_file, open(output_path, "wb") as target_file:
                target_file.write(source_file.read())
            
            print_colored(f"  - Fichier CSV sauvegardé avec succès dans : {output_path}", "green")
            return output_path

    except requests.exceptions.RequestException as e:
        print_colored(f"Erreur lors de la requête API : {e}", "fail")
        raise
    except zipfile.BadZipFile:
        print_colored("Erreur : Le fichier téléchargé n'est pas une archive ZIP valide.", "fail")
        raise
    finally:
        if os.path.exists(zip_path):
            os.remove(zip_path)
            print_colored(f"  - Fichier temporaire {zip_path} supprimé.", "green")
        print_colored("\n--- Opération terminée ---", "header")

# Cette partie ne s'exécute que si vous lancez ce script directement
if __name__ == "__main__":
    print("Ce script est conçu pour être importé. Pour tester, lancez une fonction spécifique.")
    try:
        # Test pour le téléchargement de l'inventaire principal
        download_inventory_file(endpoint="/inventory", zip_filename="inventory.zip", csv_filename="inventory.csv")
    except Exception as e:
        print(f"Le test a échoué : {e}")

