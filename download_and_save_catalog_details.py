import requests
import zipfile
import os
import io
import json
from dotenv import load_dotenv

# Charger les variables d'environnement à partir du fichier .env
load_dotenv()

def download_and_save_catalog_files(catalog_name: str):
    """
    Télécharge le fichier ZIP des pièces pour un catalogue donné en deux étapes :
    1. Récupère les métadonnées du catalogue via l'API.
    2. Télécharge l'archive ZIP depuis l'URL fournie dans les métadonnées.

    Args:
        catalog_name (str): Le nom du catalogue à télécharger (ex: 'fatbook').
    """
    # Récupération des configurations depuis les variables d'environnement.
    base_url = os.getenv("API_BASE_URL")
    bearer_token = os.getenv("PARTS_CANADA_API_TOKEN")
    target_folder = f"CATALOGUES-{catalog_name}"
    endpoint = f"/catalogues/{catalog_name}"

    if not base_url or not bearer_token:
        raise ValueError("Les variables d'environnement API_BASE_URL et PARTS_CANADA_API_TOKEN doivent être définies.")

    catalog_url = f"{base_url}{endpoint}"
    headers = {"Authorization": f"Bearer {bearer_token}"}

    print(f"Début du processus pour le catalogue '{catalog_name}'...")
    try:
        # ÉTAPE 1: Obtenir les métadonnées du catalogue depuis l'API.
        print(f"1. Récupération des informations depuis {catalog_url}")
        metadata_response = requests.get(catalog_url, headers=headers)
        metadata_response.raise_for_status()

        # ÉTAPE 2: Extraire l'URL de l'archive depuis la réponse JSON.
        try:
            metadata = metadata_response.json()
            archive_url = metadata.get('archive')
            if not archive_url:
                raise ValueError("La clé 'archive' est introuvable dans la réponse JSON de l'API.")
            print(f"2. URL de l'archive trouvée : {archive_url}")
        except json.JSONDecodeError:
            print("Erreur : La réponse de l'API n'est pas un JSON valide.")
            raise

        # ÉTAPE 3: Télécharger le fichier ZIP depuis l'URL de l'archive.
        print(f"3. Téléchargement du fichier ZIP en cours...")
        zip_response = requests.get(archive_url, stream=True)
        zip_response.raise_for_status()

        # ÉTAPE 4: Créer le dossier de destination.
        if not os.path.exists(target_folder):
            os.makedirs(target_folder)
            print(f"4. Dossier '{target_folder}' créé.")
        print("   Téléchargement du ZIP réussi.")

        # ÉTAPE 5: Décompresser le fichier ZIP.
        with zipfile.ZipFile(io.BytesIO(zip_response.content)) as zf:
            print(f"5. Décompression du catalogue '{catalog_name}'...")
            zf.extractall(target_folder)
            output_path = os.path.join(target_folder)
            print(f"   Catalogue '{catalog_name}' extrait avec succès dans '{target_folder}'.")
            return output_path
        
    except requests.exceptions.RequestException as e:
        print(f"Une erreur de réseau est survenue pour le catalogue '{catalog_name}': {e}")
        raise
    except zipfile.BadZipFile:
        print("Erreur : Le fichier téléchargé depuis l'URL de l'archive n'est pas un ZIP valide.")
        raise
    except Exception as e:
        print(f"Une erreur inattendue est survenue : {e}")
        raise


if __name__ == "__main__":
    try:
        print("Lancement du test autonome pour le téléchargement de catalogue...")
        download_and_save_catalog_files(catalog_name="snow")
        print("Test autonome terminé avec succès.")
    except Exception as e:
        print(f"Le test autonome a échoué : {e}")

