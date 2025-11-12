import os
import sys
import requests
import zipfile
from dotenv import load_dotenv

def download_inventory_file(endpoint: str):
    """
    Télécharge un fichier ZIP depuis un endpoint de l'API, le décompresse,
    et sauvegarde son contenu dans un dossier cible.
    """
    # Charger les variables d'environnement (au cas où ce module est appelé seul)
    load_dotenv() 
    
    # Récupérer les configurations depuis les variables d'environnement
    base_url = os.getenv("API_BASE_URL")
    bearer_token = os.getenv("PARTS_CANADA_API_TOKEN")
    target_folder = "INVENTAIRE-PARTS-CANADA"

    if not base_url or not bearer_token:
        raise ValueError("Les variables d'environnement API_BASE_URL et PARTS_CANADA_API_TOKEN doivent être définies.")

    inventory_url = f"{base_url}{endpoint}"
    headers = {
        "Authorization": f"Bearer {bearer_token}"
    }

    print(f"Début du téléchargement de l'inventaire depuis {inventory_url}...")

    # ÉTAPE 1: Créer le dossier cible s'il n'existe pas
    if not os.path.exists(target_folder):
        os.makedirs(target_folder)
        print(f"1/4. Dossier '{target_folder}' créé.")
    else:
        print(f"1/4. Le dossier '{target_folder}' existe déjà.")

    # ÉTAPE 2: Télécharger le fichier ZIP dans un fichier temporaire
    print(f"2/4. Téléchargement du fichier ZIP en cours...")
    zip_response = requests.get(inventory_url, headers=headers, stream=True)
    zip_response.raise_for_status()
    
    temp_zip_path = os.path.join(target_folder, "temp_inventory.zip")
    total_size = zip_response.headers.get('content-length')

    with open(temp_zip_path, 'wb') as f:
        if total_size is None:
            f.write(zip_response.content)
            print("   Téléchargement du ZIP réussi (taille inconnue).")
        else:
            total_size = int(total_size)
            downloaded = 0
            chunk_size = 128 * 1024
            
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

    # ÉTAPE 3 & 4: Décompresser et supprimer le fichier temporaire
    try:
        with zipfile.ZipFile(temp_zip_path, 'r') as zf:
            print(f"3/4. Décompression du fichier en cours...")
            zf.extractall(target_folder)
            output_path = os.path.join(target_folder)
            print(f"   Fichiers extraits avec succès dans le dossier '{target_folder}'.")
    finally:
        # S'assurer que le fichier temporaire est supprimé
        os.remove(temp_zip_path)
        print(f"4/4. Fichier temporaire '{os.path.basename(temp_zip_path)}' supprimé.")
    
    return output_path

# Ce bloc permet de tester ce module spécifiquement
if __name__ == "__main__":
    print("Test du module de téléchargement en mode autonome...")
    try:
        download_inventory_file(endpoint="/inventory")
        print("Test de téléchargement réussi.")
    except Exception as e:
        print(f"Test de téléchargement a échoué : {e}")