import requests
import zipfile
import os
import io
from dotenv import load_dotenv

# Charger les variables d'environnement à partir du fichier .env
load_dotenv()

def download_inventory_file(endpoint: str):
    """
    Télécharge un fichier ZIP depuis un endpoint de l'API, le décompresse,
    et sauvegarde son contenu dans un dossier cible.

    Args:
        endpoint (str): Le chemin de l'API à appeler (ex: "/inventory").

    Returns:
        str: Le chemin complet du fichier CSV extrait.
    """
    # Récupérer les configurations depuis les variables d'environnement
    base_url = os.getenv("API_BASE_URL")
    bearer_token = os.getenv("PARTS_CANADA_API_TOKEN")
    target_folder = os.getenv("DOWNLOAD_FOLDER", "DONNÉES-TÉLÉCHARGÉES")

    if not base_url or not bearer_token:
        raise ValueError("Les variables d'environnement API_BASE_URL et PARTS_CANADA_API_TOKEN doivent être définies.")

    inventory_url = f"{base_url}{endpoint}"
    headers = {
        "Authorization": f"Bearer {bearer_token}"
    }

    print(f"Début du téléchargement depuis {inventory_url}...")

    try:
        # Étape 1 : Télécharger le fichier
        response = requests.get(inventory_url, headers=headers, stream=True)

        # Vérifier si la requête a réussi (code de statut HTTP 200)
        response.raise_for_status()

        print("Téléchargement réussi.")

        # Étape 2 : Créer le dossier cible s'il n'existe pas
        if not os.path.exists(target_folder):
            os.makedirs(target_folder)
            print(f"Dossier '{target_folder}' créé.")

        # Étape 3 : Décompresser le fichier et trouver le nom du CSV
        with zipfile.ZipFile(io.BytesIO(response.content)) as zf:
            print("Décompression du fichier en cours...")

            # Extrait tous les fichiers
            zf.extractall(target_folder)
            
            output_path = os.path.join(target_folder)
            print(f"Fichier  extrait et sauvegardé avec succès dans le dossier '{target_folder}'.")
            return output_path

    except requests.exceptions.RequestException as e:
        print(f"Une erreur de réseau est survenue : {e}")
        raise  # Propage l'erreur pour que l'API Flask puisse la gérer
    except zipfile.BadZipFile:
        print("Erreur : Le fichier téléchargé n'est pas un fichier ZIP valide.")
        raise
    except Exception as e:
        print(f"Une erreur inattendue est survenue : {e}")
        raise

if __name__ == "__main__":
    # Ce bloc permet de tester le script de manière autonome
    try:
        print("Test du module de téléchargement en mode autonome...")
        download_inventory_file(
            endpoint="/inventory"
        )
    except Exception as e:
        print(f"Le test autonome a échoué : {e}")
