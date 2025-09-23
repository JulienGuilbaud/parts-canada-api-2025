import os
import datetime

def get_folder_content(folder_name):
    """
    Analyse un dossier et retourne les propriétés des fichiers et dossiers qu'il contient.
    """
    items_properties = []
    if os.path.exists(folder_name):
        for item_name in os.listdir(folder_name):
            item_path = os.path.join(folder_name, item_name)
            try:
                stats = os.stat(item_path)
                mod_time = datetime.datetime.fromtimestamp(stats.st_mtime).strftime('%Y-%m-%d %H:%M:%S')

                if os.path.isfile(item_path):
                    item_type = 'Fichier'
                    size_mo = round(stats.st_size / (1024 * 1024), 2)
                elif os.path.isdir(item_path):
                    item_type = 'Dossier'
                    size_mo = '-' # Les dossiers n'ont pas de taille directe
                else:
                    continue # Ignorer les autres types (liens symboliques, etc.)

                items_properties.append({
                    'name': item_name,
                    'type': item_type,
                    'mod_date': mod_time,
                    'size_mo': size_mo
                })
            except Exception as e:
                print(f"Impossible de lire les propriétés de {item_name}: {e}")
    return items_properties

if __name__ == "__main__":
    # Ce bloc est exécuté uniquement lorsque le script est lancé directement.
    # Il sert à tester la fonction get_folder_content de manière autonome.
    

    # 1. Définir et créer un environnement de test.
    test_folder = "CATALOGUES-snow"
    

    print(f"--- Début du test pour get_folder_content ---")
    

    # 2. Appeler la fonction à tester sur le dossier existant.
    print(f"\nAppel de get_folder_content('{test_folder}')...")
    folder_contents = get_folder_content(test_folder)
    print(f"Contenu du dossier '{test_folder}':")
    print(folder_contents)
    print(f"--- Fin du test pour get_folder_content ---")



