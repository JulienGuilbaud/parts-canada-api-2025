import requests
import zipfile
import os
import sys
from dotenv import load_dotenv

# Charger les variables d'environnement à partir du fichier .env
load_dotenv()

def download_extended_inventory_file():
    """
    Télécharge le fichier ZIP de l'inventaire étendu, le décompresse,
    et le sauvegarde dans un dossier cible.
    """
    # Récupérer les configurations depuis les variables d'environnement
    base_url = os.getenv("API_BASE_URL")
    bearer_token = os.getenv("PARTS_CANADA_API_TOKEN")
    target_folder = "INVENTAIRE-ETENDU-PARTS-CANADA"
    endpoint = "/inventory/extended" # Cible le nouvel endpoint

    if not base_url or not bearer_token:
        raise ValueError("Les variables d'environnement API_BASE_URL et PARTS_CANADA_API_TOKEN doivent être définies.")

    inventory_url = f"{base_url}{endpoint}"
    headers = {
        "Authorization": f"Bearer {bearer_token}"
    }

    # Nom du fichier ZIP temporaire
    temp_zip_path = os.path.join(target_folder, "extended_inventory_temp.zip")

    print(f"Début du téléchargement depuis {inventory_url}...")

    try:
        # Étape 1 : Créer le dossier cible s'il n'existe pas
        if not os.path.exists(target_folder):
            os.makedirs(target_folder)
            print(f"1/4. Dossier '{target_folder}' créé.")
        else:
            print(f"1/4. Le dossier '{target_folder}' existe déjà.")

        # Étape 2 : Télécharger le fichier ZIP
        print("2/4. Téléchargement du fichier ZIP en cours...")
        with requests.get(inventory_url, headers=headers, stream=True) as response:
            response.raise_for_status()
            
            total_size = int(response.headers.get('content-length', 0))
            downloaded_size = 0
            chunk_size = 1024 * 128  # 128 Ko

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

        # Étape 3 : Décompresser le fichier ZIP
        print("3/4. Décompression du fichier en cours...")
        with zipfile.ZipFile(temp_zip_path, 'r') as zf:
            zf.extractall(target_folder)
            
            # Supposer que le premier fichier .csv est celui que nous voulons
            csv_filename = [name for name in zf.namelist() if name.endswith('.csv')][0]
            output_path = os.path.join(target_folder, csv_filename)
            
            print(f"     Fichier extrait avec succès dans '{target_folder}'.")

        # Étape 4 : Nettoyage
        print("4/4. Nettoyage du fichier ZIP temporaire...")
        os.remove(temp_zip_path)
        print(f"     '{temp_zip_path}' supprimé.")

        return output_path

    except requests.exceptions.RequestException as e:
        print(f"Une erreur de réseau est survenue : {e}")
        raise
    except zipfile.BadZipFile:
        print("Erreur : Le fichier téléchargé n'est pas un fichier ZIP valide.")
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

# Ce bloc permet de tester le script de manière autonome
if __name__ == "__main__":
    try:
        print("Test du module de téléchargement de l'inventaire étendu...")
        download_extended_inventory_file()
    except Exception as e:
        print(f"Le test autonome a échoué : {e}")
