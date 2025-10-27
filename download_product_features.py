import requests
import zipfile
import os
import sys
from dotenv import load_dotenv

# Charger les variables d'environnement à partir du fichier .env
load_dotenv()

def download_product_features_file(catalog_name: str):
    """
    Télécharge le fichier ZIP des 'features' pour un catalogue spécifique
    et l'extrait directement dans le dossier parent du catalogue.

    Args:
        catalog_name (str): Le nom du catalogue (ex: "snow", "fatbook").
    """
    # Récupérer les configurations depuis les variables d'environnement
    base_url = os.getenv("API_BASE_URL")
    bearer_token = os.getenv("PARTS_CANADA_API_TOKEN")

    # --- MODIFICATION ---
    # Le dossier cible est maintenant le dossier parent du catalogue
    target_folder = f"CATALOGUES-{catalog_name}"
    # --- FIN MODIFICATION ---

    endpoint = f"/products/features/{catalog_name}/download"

    if not base_url or not bearer_token:
        raise ValueError("Les variables d'environnement API_BASE_URL et PARTS_CANADA_API_TOKEN doivent être définies.")

    # Ajouter un paramètre 'start_date' pour forcer un téléchargement complet
    params = {
        "start_date": "2000-01-01"
    }

    features_url = f"{base_url}{endpoint}"
    headers = {
        "Authorization": f"Bearer {bearer_token}"
    }

    # Nom du fichier ZIP temporaire (placé dans le dossier cible)
    # --- MODIFICATION ---
    # S'assurer que le dossier cible existe avant de définir le chemin temporaire
    if not os.path.exists(target_folder):
         os.makedirs(target_folder)
         print(f"Dossier '{target_folder}' créé (pour fichier temporaire).") # Message ajusté
    temp_zip_path = os.path.join(target_folder, f"{catalog_name}_features_temp.zip")
    # --- FIN MODIFICATION ---


    print(f"Début du téléchargement des features pour '{catalog_name}' depuis {features_url}...")

    try:
        # Étape 1 : Vérifier/Créer le dossier cible (déplacé avant temp_zip_path)
        # --- MODIFICATION ---
        # Cette vérification est maintenant faite avant la définition de temp_zip_path
        # On ajuste juste le message ici si le dossier existe déjà
        if os.path.exists(target_folder):
             print(f"1/4. Le dossier '{target_folder}' existe déjà.")
        # --- FIN MODIFICATION ---


        # Étape 2 : Télécharger le fichier ZIP
        print("2/4. Téléchargement du fichier ZIP en cours...")
        downloaded_size = 0
        chunk_size = 1024 * 128  # 128 Ko
        update_interval = 5
        chunk_count = 0

        with requests.get(features_url, headers=headers, params=params, stream=True) as response:
            response.raise_for_status()
            content_type = response.headers.get('content-type', '').lower()

            if 'application/octet-stream' not in content_type and 'application/zip' not in content_type:
                response_text = response.text
                print(f"\n     Info: Le serveur a répondu (pas un fichier ZIP) : {response_text}")
                try:
                    json_response = response.json()
                    print(f"     Message JSON reçu: {json_response}")
                except requests.exceptions.JSONDecodeError:
                    pass
                return

            total_size = int(response.headers.get('content-length', 0))

            with open(temp_zip_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=chunk_size):
                    if chunk:
                        f.write(chunk)
                        downloaded_size += len(chunk)
                        chunk_count += 1
                        if chunk_count % update_interval == 0 or downloaded_size == total_size:
                           progress = (downloaded_size / total_size) * 100 if total_size > 0 else 0
                           downloaded_mb = downloaded_size / (1024 * 1024)
                           total_mb = total_size / (1024 * 1024)
                           print(f"\r     [{'=' * int(progress / 4):<25}] {downloaded_mb:.2f} Mo / {total_mb:.2f} Mo", end='')

        print()
        print("     Téléchargement du ZIP réussi.")

        # Étape 3 : Décompresser le fichier ZIP
        print("3/4. Décompression du fichier en cours...")
        with zipfile.ZipFile(temp_zip_path, 'r') as zf:
            # --- MODIFICATION ---
            # Extrait directement dans target_folder (qui est maintenant le dossier parent)
            zf.extractall(target_folder)
            print(f"     Fichiers extraits avec succès dans '{target_folder}'.")
            # --- FIN MODIFICATION ---

        # Étape 4 : Nettoyage
        print("4/4. Nettoyage du fichier ZIP temporaire...")
        os.remove(temp_zip_path)
        print(f"     '{temp_zip_path}' supprimé.")

        return target_folder

    except requests.exceptions.RequestException as e:
        print(f"\nUne erreur de réseau est survenue : {e}")
        raise
    except zipfile.BadZipFile:
        print("\nErreur : Le fichier téléchargé n'est pas un fichier ZIP valide.")
        # Nettoyer le fichier corrompu si possible
        if os.path.exists(temp_zip_path):
             try:
                 os.remove(temp_zip_path)
                 print(f"Nettoyage : Fichier ZIP temporaire corrompu '{temp_zip_path}' supprimé.")
             except Exception as clean_e:
                 print(f"Erreur lors du nettoyage du fichier ZIP corrompu : {clean_e}")
        raise
    except Exception as e:
        print(f"\nUne erreur inattendue est survenue : {e}")
        raise
    finally:
        # Assurer la suppression finale du fichier temporaire
        if os.path.exists(temp_zip_path):
            try:
                os.remove(temp_zip_path)
                print(f"Nettoyage (finally) : '{temp_zip_path}' supprimé.")
            except Exception as e:
                print(f"Erreur lors du nettoyage final du fichier temporaire : {e}")


if __name__ == "__main__":
    try:
        print("Test du module de téléchargement des product features...")
        download_product_features_file(catalog_name="fatbook") # Teste avec fatbook
        print("\nTest autonome terminé.")
    except Exception as e:
        print(f"\nLe test autonome a échoué : {e}")

