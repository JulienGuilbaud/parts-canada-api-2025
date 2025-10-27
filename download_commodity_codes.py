import requests
import zipfile
import os
import sys  # Ajouté pour la barre de progression
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

def download_commodity_codes_file():
    """
    Télécharge le fichier ZIP contenant les codes de commodité (catégories de produits).
    """
    base_url = os.getenv("API_BASE_URL")
    bearer_token = os.getenv("PARTS_CANADA_API_TOKEN")
    target_folder = "COMMODITY-CODES"
    endpoint = "/products/commodity-codes/download"

    if not base_url or not bearer_token:
        raise ValueError("Les variables d'environnement API_BASE_URL et PARTS_CANADA_API_TOKEN doivent être définies.")

    url = f"{base_url}{endpoint}"
    headers = {"Authorization": f"Bearer {bearer_token}"}

    print(f"Début du téléchargement des codes de commodité depuis {url}...")
    try:
        # ÉTAPE 1: Créer le dossier cible s'il n'existe pas
        if not os.path.exists(target_folder):
            os.makedirs(target_folder)
            print(f"1/4. Dossier '{target_folder}' créé.")
        else:
            print(f"1/4. Le dossier '{target_folder}' existe déjà.")

        # --- Début de la modification ---

        # ÉTAPE 2: Télécharger le fichier ZIP dans un fichier temporaire
        print(f"2/4. Téléchargement du fichier ZIP en cours...")
        response = requests.get(url, headers=headers, stream=True)
        response.raise_for_status()

        temp_zip_path = os.path.join(target_folder, "temp_codes.zip")
        total_size = response.headers.get('content-length')

        with open(temp_zip_path, 'wb') as f:
            if total_size is None:
                f.write(response.content)
                print("   Téléchargement du ZIP réussi (taille inconnue).")
            else:
                total_size = int(total_size)
                downloaded = 0
                chunk_size = 128 * 1024  # Modification: 1 Mo -> 128 Ko
                
                for data in response.iter_content(chunk_size=chunk_size):
                    downloaded += len(data)
                    f.write(data)
                    
                    progress = int(50 * downloaded / total_size)
                    megabytes_downloaded = downloaded / (1024 * 1024)
                    total_megabytes = total_size / (1024 * 1024)
                    
                    sys.stdout.write(f"\r   [{'=' * progress}{' ' * (50 - progress)}] {megabytes_downloaded:.2f} Mo / {total_megabytes:.2f} Mo")
                    sys.stdout.flush()
                
                sys.stdout.write('\n')
                print("   Téléchargement du ZIP terminé.")

        # --- Fin de la modification ---

        # ÉTAPE 3 & 4: Décompresser et supprimer le fichier temporaire
        try:
            with zipfile.ZipFile(temp_zip_path, 'r') as zf:
                print(f"3/4. Décompression du fichier en cours...")
                zf.extractall(target_folder)
        finally:
            # S'assurer que le fichier temporaire est supprimé
            os.remove(temp_zip_path)
            print(f"4/4. Fichier temporaire '{os.path.basename(temp_zip_path)}' supprimé.")
            
        print(f"Fichiers extraits avec succès dans le dossier '{target_folder}'.")
        return target_folder

    except requests.exceptions.RequestException as e:
        print(f"Une erreur de réseau est survenue : {e}")
        raise
    except zipfile.BadZipFile:
        print("Erreur : Le fichier téléchargé n'est pas un fichier ZIP valide.")
        raise
    except Exception as e:
        print(f"Une erreur inattendue est survenue : {e}")
        raise

if __name__ == "__main__":
    try:
        print("Test du module de téléchargement des codes de commodité...")
        download_commodity_codes_file()
    except Exception as e:
        print(f"Le test autonome a échoué : {e}")


