import requests
import zipfile
import os
# Le module 'io' n'est plus nécessaire
import json
import sys
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
        # ÉTAPE 1: Créer le dossier de destination si il n'existe pas
        if not os.path.exists(target_folder):
            os.makedirs(target_folder)
            print(f"1/5. Dossier '{target_folder}' créé.")
        else:
            print(f"1/5. Le dossier '{target_folder}' existe déjà.")

        # ÉTAPE 2: Obtenir les métadonnées du catalogue depuis l'API.
        print(f"2/5. Récupération des informations depuis {catalog_url}")
        metadata_response = requests.get(catalog_url, headers=headers)
        metadata_response.raise_for_status()

        # ÉTAPE 3: Extraire l'URL de l'archive depuis la réponse JSON.
        try:
            metadata = metadata_response.json()
            archive_url = metadata.get('archive')
            if not archive_url:
                raise ValueError("La clé 'archive' est introuvable dans la réponse JSON de l'API.")
            print(f"3/5. URL de l'archive trouvée : {archive_url}")
        except json.JSONDecodeError:
            print("Erreur : La réponse de l'API n'est pas un JSON valide.")
            raise

        # --- Début de la modification : suppression de 'io' ---

        # ÉTAPE 4: Télécharger le contenu dans un fichier ZIP temporaire.
        print(f"4/5. Téléchargement du fichier ZIP en cours...")
        zip_response = requests.get(archive_url, stream=True)
        zip_response.raise_for_status()
        
        temp_zip_path = os.path.join(target_folder, f"temp_{catalog_name}.zip")
        total_size = zip_response.headers.get('content-length')

        with open(temp_zip_path, 'wb') as f:
            if total_size is None:
                f.write(zip_response.content)
                print("   Téléchargement du ZIP réussi (taille inconnue).")
            else:
                total_size = int(total_size)
                downloaded = 0
                chunk_size = 1024 * 1024  # 1 MB
                
                for data in zip_response.iter_content(chunk_size=chunk_size):
                    downloaded += len(data)
                    f.write(data)
                    
                    progress = int(50 * downloaded / total_size)
                    megabytes_downloaded = downloaded / (1024 * 1024)
                    total_megabytes = total_size / (1024 * 1024)
                    
                    sys.stdout.write(f"\r   [{'=' * progress}{' ' * (50 - progress)}] {megabytes_downloaded:.2f} Mo / {total_megabytes:.2f} Mo")
                    sys.stdout.flush()
                
                sys.stdout.write('\n')
                print("   Téléchargement du ZIP terminé.")

        # ÉTAPE 5: Décompresser depuis le fichier temporaire et le supprimer.
        try:
            with zipfile.ZipFile(temp_zip_path, 'r') as zf:
                print(f"5/5. Décompression du catalogue '{catalog_name}'...")
                zf.extractall(target_folder)
                output_path = os.path.join(target_folder)
                print(f"   Catalogue '{catalog_name}' extrait avec succès dans '{target_folder}'.")
        finally:
            # S'assurer que le fichier temporaire est supprimé même si la décompression échoue
            os.remove(temp_zip_path)
            print(f"   Fichier temporaire '{os.path.basename(temp_zip_path)}' supprimé.")
        
        return output_path
        
        # --- Fin de la modification ---

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

