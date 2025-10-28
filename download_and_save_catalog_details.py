import requests
import zipfile
import os
import sys
from dotenv import load_dotenv

from download_product_features import download_product_features_file

# Charger les variables d'environnement à partir du fichier .env
load_dotenv()

def download_and_save_catalog_files(catalog_name: str):
    """
    Télécharge le fichier ZIP des pièces pour un catalogue donné,
    PUIS déclenche le téléchargement des 'product features' associées.
    """
    # Récupération des configurations
    base_url = os.getenv("API_BASE_URL")
    bearer_token = os.getenv("PARTS_CANADA_API_TOKEN")
    target_folder = f"CATALOGUES-{catalog_name}"
    endpoint = f"/catalogues/{catalog_name}"

    if not base_url or not bearer_token:
        raise ValueError("Les variables d'environnement API_BASE_URL et PARTS_CANADA_API_TOKEN doivent être définies.")

    catalog_url = f"{base_url}{endpoint}"
    headers = {"Authorization": f"Bearer {bearer_token}"}

    # Nom du fichier ZIP temporaire
    temp_zip_path = os.path.join(target_folder, f"{catalog_name}_temp.zip")

    print(f"Début du processus pour le catalogue '{catalog_name}'...")
    try:
        # ÉTAPE 1: Créer le dossier de destination
        if not os.path.exists(target_folder):
            os.makedirs(target_folder)
            print(f"1/6. Dossier '{target_folder}' créé.")
        else:
            print(f"1/6. Le dossier '{target_folder}' existe déjà.")

        # ÉTAPE 2: Obtenir les métadonnées du catalogue
        print(f"2/6. Récupération des informations depuis {catalog_url}")
        metadata_response = requests.get(catalog_url, headers=headers)
        metadata_response.raise_for_status()

        # ÉTAPE 3: Extraire l'URL de l'archive
        try:
            metadata = metadata_response.json()
            archive_url = metadata.get('archive')
            if not archive_url:
                raise ValueError("La clé 'archive' est introuvable dans la réponse JSON de l'API.")
            print(f"3/6. URL de l'archive trouvée : {archive_url}")
        except Exception as e:
            print(f"Erreur lors de l'analyse JSON : {e}")
            raise

        # ÉTAPE 4: Télécharger le fichier ZIP
        print("4/6. Téléchargement du fichier ZIP du catalogue...")
        with requests.get(archive_url, headers={}, stream=True) as response:
            response.raise_for_status()
            
            total_size = int(response.headers.get('content-length', 0))
            downloaded_size = 0
            chunk_size = 1024 * 1024  # 1 Mo (conservé car les catalogues sont volumineux)

            with open(temp_zip_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=chunk_size):
                    f.write(chunk)
                    downloaded_size += len(chunk)
                    
                    # Affichage de la progression
                    progress = (downloaded_size / total_size) * 100 if total_size > 0 else 0
                    downloaded_mb = downloaded_size / (1024 * 1024)
                    total_mb = total_size / (1024 * 1024)
                    
                    sys.stdout.write(f"\r     [{'=' * int(progress / 4):<25}] {downloaded_mb:.2f} Mo / {total_mb:.2f} Mo")
                    sys.stdout.flush()
        
        print("\n     Téléchargement du ZIP réussi.")

        # ÉTAPE 5: Décompresser le fichier ZIP
        print(f"5/6. Décompression du catalogue '{catalog_name}'...")
        with zipfile.ZipFile(temp_zip_path, 'r') as zf:
            zf.extractall(target_folder)
            
            # Supposer que le premier fichier .csv est celui que nous voulons
            csv_filename = [name for name in zf.namelist() if name.endswith('.csv')][0]
            output_path = os.path.join(target_folder, csv_filename)
            
            print(f"     Catalogue '{catalog_name}' extrait avec succès dans '{target_folder}'.")

        # ÉTAPE 6: Nettoyage
        print("6/6. Nettoyage du fichier ZIP temporaire...")
        os.remove(temp_zip_path)
        print(f"     '{temp_zip_path}' supprimé.")

        # --- NOUVELLE ÉTAPE (AUTOMATISÉE) ---
        print(f"\n7/7. Lancement du téléchargement des 'product features' pour '{catalog_name}'...")
        try:
            download_product_features_file(catalog_name)
            print(f"     Téléchargement des 'features' pour '{catalog_name}' terminé.")
        except Exception as e:
            # Ne pas faire planter le script principal si les features échouent
            print(f"     AVERTISSEMENT : Échec du téléchargement des 'features' : {e}")
        # --- FIN DE L'AJOUT ---

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
    finally:
        # Assurer la suppression du fichier temporaire même en cas d'erreur
        if os.path.exists(temp_zip_path):
            try:
                os.remove(temp_zip_path)
                print(f"Nettoyage (finally) : '{temp_zip_path}' supprimé.")
            except Exception as e:
                print(f"Erreur lors du nettoyage du fichier temporaire : {e}")

# Test avec un catalogue (ex: "snow")
if __name__ == "__main__":
    try:
        print("Lancement du test autonome pour le téléchargement de catalogue...")
       
        download_and_save_catalog_files(catalog_name="snow")
        print("Test autonome terminé avec succès.")
    except Exception as e:
        print(f"Le test autonome a échoué : {e}")

