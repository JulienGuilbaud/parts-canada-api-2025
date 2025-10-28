import os
import glob
import csv

# Définir le dossier de travail
COMMODITY_FOLDER = "COMMODITY-CODES"

def find_csv_file(folder_path, file_pattern="*.csv"):
    """
    Trouve le premier fichier .csv dans un dossier.
    """
    csv_files = glob.glob(os.path.join(folder_path, file_pattern))
    if not csv_files:
        raise FileNotFoundError(f"Aucun fichier CSV trouvé dans le dossier {folder_path}")
    
    # Exclure le fichier de sortie s'il existe déjà
    for f in csv_files:
        if "fusionnes" not in f:
            return f
    
    if not csv_files:
         raise FileNotFoundError(f"Fichier source CSV non trouvé dans {folder_path}")
    return csv_files[0]


def transformer_codes_commodite():
    """
    Lit le fichier commodity_codes.csv original, fusionne les colonnes parent/enfant
    et écrit le résultat dans un nouveau fichier CSV.
    """
    
    try:
        source_file = find_csv_file(COMMODITY_FOLDER, "commodity_codes.csv")
        output_file = os.path.join(COMMODITY_FOLDER, "commodity_codes_fusionnes.csv")
        
        print(f"Début de la transformation : '{source_file}'...")

        with open(source_file, mode='r', encoding='utf-8-sig') as infile:
            reader = csv.reader(infile)
            
            with open(output_file, mode='w', newline='', encoding='utf-8') as outfile:
                writer = csv.writer(outfile)
                
                # Écrire le nouvel en-tête
                writer.writerow(["Combined Code", "Combined Description"])
                
                # Lire l'en-tête original pour le sauter
                header = next(reader)
                
                # Traiter chaque ligne
                for row in reader:
                    try:
                        # Assurer que la ligne a bien 4 colonnes
                        if len(row) == 4:
                            parent_code = row[0].strip()
                            parent_desc = row[1].strip()
                            child_code = row[2].strip()
                            child_desc = row[3].strip()
                            
                            # Créer les nouvelles colonnes
                            combined_code = parent_code + child_code
                            combined_desc = f"{parent_desc} : {child_desc}"
                            
                            # Écrire la nouvelle ligne
                            writer.writerow([combined_code, combined_desc])
                    except Exception as e:
                        print(f"Erreur lors du traitement de la ligne {row}: {e}")
                        
        print(f"Transformation terminée. Fichier sauvegardé : '{output_file}'")
        return output_file

    except FileNotFoundError as e:
        print(f"Erreur : {e}")
    except Exception as e:
        print(f"Une erreur inattendue est survenue lors de la transformation : {e}")
        raise

# Test autonome du module
if __name__ == "__main__":

    print("--- Test de transformation des codes de commodité ---")
    try:
        transformer_codes_commodite()
    except Exception as e:
        print(f"Le test autonome a échoué : {e}")
