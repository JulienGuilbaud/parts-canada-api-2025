import requests
import os
import zipfile
from dotenv import load_dotenv

# --- Configuration ---
# Charge les variables d'environnement à partir du fichier .env
load_dotenv()

# Récupère la clé d'API depuis la variable d'environnement PARTS_CANADA_API_KEY
API_KEY = os.environ.get('PARTS_CANADA_API_KEY')

# URL de base pour l'environnement de développement (Sandbox)
BASE_URL = "https://sandbox-api.partscanada.com/api/v2"

# Dossier de destination pour les fichiers extraits
OUTPUT_DIR = "source"
ZIP_FILENAME = "inventory.zip"
CSV_FILENAME = "inventory.csv"

# --- Fonctions ---

def print_colored(text, color):
    """Affiche du texte en couleur dans le terminal."""
    colors = {
        "header": "\033[95m", "blue": "\033[94m", "green": "\033[92m",
        "warning": "\033[93m", "fail": "\033[91m", "endc": "\033[0m", "bold": "\033[1m"
    }
    print(f"{colors.get(color, '')}{text}{colors['endc']}")

def download_and_save_inventory():
    """
    Télécharge, décompresse et enregistre le fichier d'inventaire
    dans le dossier 'source'.
    """
    print_colored("--- Lancement du téléchargement de l'inventaire ---", "header")

    # Vérification de la clé d'API
    if not API_KEY:
        print_colored("Erreur : La clé d'API (PARTS_CANADA_API_KEY) n'est pas définie.", "fail")
        print_colored("Veuillez la définir dans votre fichier .env.", "warning")
        return

    # Création du dossier 'source' s'il n'existe pas
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        print_colored(f"  - Dossier '{OUTPUT_DIR}' créé.", "green")

    # Préparation de la requête
    endpoint = "/inventory"
    url = f"{BASE_URL}{endpoint}"
    headers = {'Authorization': f'Bearer {API_KEY}'}
    zip_path = os.path.join(OUTPUT_DIR, ZIP_FILENAME)

    try:
        # Étape 1: Télécharger et enregistrer le fichier ZIP
        print_colored(f"> Appel de l'API : {url}", "blue")
        response = requests.get(url, headers=headers, timeout=60, stream=True)
        response.raise_for_status()
        
        with open(zip_path, 'wb') as f:
            f.write(response.content)
        print_colored(f"  - Fichier ZIP sauvegardé dans : {zip_path}", "green")

        # Étape 2: Décompresser le fichier ZIP depuis le disque
        print_colored(f"> Décompression de {zip_path}...", "blue")
        with zipfile.ZipFile(zip_path, 'r') as z:
            csv_internal_path = next((name for name in z.namelist() if name.lower().endswith('.csv')), None)
            
            if not csv_internal_path:
                print_colored("Erreur : Aucun fichier CSV trouvé dans l'archive ZIP.", "fail")
                return

            print_colored(f"  - Fichier CSV trouvé dans l'archive : {csv_internal_path}", "green")

            # Étape 3: Extraire et enregistrer le fichier CSV
            output_path = os.path.join(OUTPUT_DIR, CSV_FILENAME)
            with z.open(csv_internal_path) as source_file, open(output_path, "wb") as target_file:
                target_file.write(source_file.read())
            
            print_colored(f"  - Fichier CSV sauvegardé avec succès dans : {output_path}", "green")

    except requests.exceptions.RequestException as e:
        print_colored(f"Erreur lors de la requête API : {e}", "fail")
    except zipfile.BadZipFile:
        print_colored("Erreur : Le fichier téléchargé n'est pas une archive ZIP valide.", "fail")
    except Exception as e:
        print_colored(f"Une erreur inattendue est survenue : {e}", "fail")
    finally:
        # Étape 4: Nettoyage du fichier ZIP
        if os.path.exists(zip_path):
            os.remove(zip_path)
            print_colored(f"  - Fichier temporaire {zip_path} supprimé.", "green")


    print_colored("\n--- Opération terminée ---", "header")

# --- Point d'entrée du script ---
if __name__ == "__main__":
    download_and_save_inventory()
