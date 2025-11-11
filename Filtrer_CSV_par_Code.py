import pandas as pd
import os

# --- Configuration ---
# Chemin vers votre fichier CSV d'origine
FICHIER_ENTREE = r"INVENTAIRE-PARTS-CANADA\PartsCanadaCSV_8374000.csv"

# Répertoire où les fichiers filtrés seront sauvegardés
REPERTOIRE_SORTIE = r"MICPARTSONLINE"

# Le code "Commodity" que vous souhaitez filtrer par défaut
CODE_A_FILTRER_DEFAUT = "1240"



def filtrer_par_code(target_code: str):
    """
    Lit un fichier CSV, le filtre par 'Commodity Code', le transforme
    pour l'import Odoo et sauvegarde le résultat.
    
    Args:
        target_code (str): Le code "Commodity" à utiliser pour le filtre.
    """
    
    # 1. Vérifier si le fichier d'entrée existe
    if not os.path.exists(FICHIER_ENTREE):
        print(f"Erreur : Le fichier d'entrée '{FICHIER_ENTREE}' n'a pas été trouvé.")
        return

    # 2. Définir le chemin de sortie
    # Le nom du fichier sera (par ex): MICPARTSONLINE\parts_canada_1240.csv
    output_file = os.path.join(REPERTOIRE_SORTIE, f"parts_canada_{target_code}.csv")

    print(f"Démarrage du filtre pour le code '{target_code}'...")
    print(f"Lecture de : {FICHIER_ENTREE}")

    try:
        # 3. Lire le fichier CSV avec pandas
        # On spécifie dtype pour s'assurer que les codes sont lus comme du texte.
        df = pd.read_csv(FICHIER_ENTREE, dtype={
            'Commodity Code': str, 
            'Part Number': str,
            'Manufacturer Part Number': str  # Ajout pour la concaténation
        })

        # 4. Vérifier si la colonne nécessaire existe
        if 'Commodity Code' not in df.columns:
            print(f"Erreur : Colonne 'Commodity Code' introuvable dans le fichier.")
            print(f"Colonnes disponibles : {df.columns.tolist()}")
            return

        # 5. Appliquer le filtre
        df_filtre = df[df['Commodity Code'] == target_code]
        
        if df_filtre.empty:
            print(f"Avertissement : Aucun produit trouvé pour le code '{target_code}'.")
        else:
            print(f"{len(df_filtre)} produits trouvés. Transformation pour Odoo...")

        # 6. Transformer pour Odoo
        # Créer un nouveau DataFrame vide pour le format Odoo
        df_odoo = pd.DataFrame()
        
        # Remplir les colonnes dans l'ordre Odoo
        # .fillna() est utilisé pour éviter les erreurs si des données sont manquantes
        
        df_odoo['Name'] = df_filtre['Description EN'].fillna('')
        df_odoo['Internal Reference'] = '10-'+ df_filtre['Part Number'].fillna('')
        df_odoo['Brand'] = df_filtre['Brand'].fillna('')
        # Remplissage par default
        df_odoo['Can be Sold'] = True
        df_odoo['Can be Purchased'] = True
        df_odoo['Is Publish'] = True
        df_odoo['Product Category'] = 'New Parts'
        df_odoo['Product Type'] = 'Storable Product'
        #Remplissge du prix
        df_odoo['Sales Price'] = df_filtre['MSRP Latest'].fillna(0)
        df_odoo['Detailed Price'] = df_filtre['MSRP Latest'].fillna(0) # CORRECTION: MSAP -> MSRP
        df_odoo['Cost'] = df_filtre['Dealer Discounted Price'].fillna(0)
        # Remplissage par default
        df_odoo['Unit of Measure'] = 'Units'
        df_odoo['Customer Taxes'] = 'Tax Exempt'
        df_odoo['Vendor Taxes'] = 'Tax - Exempt'
        df_odoo['Invoicing Policy'] = 'Ordered quantities'
        df_odoo['Control Policy'] = 'On received quantities'
        df_odoo['Routes'] = 'Buy'
        df_odoo['Tracking'] = 'No Tracking'
        df_odoo['Variant Seller/Vendor'] = 'Parts Canada'
        df_odoo['Variant Seller/Delivery Lead Time'] = 0
        df_odoo['Variant Seller/Quantity'] = 0
        df_odoo['Variant Seller/Price'] = 0
        
        # Remplissage CUSTOM
        
        # --- MODIFICATION ICI ---
        # Construit la description 'en' selon votre format
        df_odoo['description_en'] = (
            df_filtre['Description Long EN'].fillna('') +
            '<br />' + 
            df_filtre['Brand'].fillna('') + ' ' +
            df_filtre['Manufacturer Part Number'].fillna('') + ' ' +
            df_filtre['Description EN'].fillna('')
        )
        # --- FIN MODIFICATION ---


        # --- MODIFICATION ICI pour description_fr ---
        # Préparer les descriptions FR avec fallback en EN si elles sont vides
        desc_long_fr_with_fallback = df_filtre['Description Long FR'].fillna(df_filtre['Description Long EN'])
        desc_fr_with_fallback = df_filtre['Description FR'].fillna(df_filtre['Description EN'])
        
        # Construit la description 'fr' avec la même structure
        df_odoo['description_fr'] = (
            desc_long_fr_with_fallback.fillna('') +
            '<br />' + 
            df_filtre['Brand'].fillna('') + ' ' +
            df_filtre['Manufacturer Part Number'].fillna('') + ' ' +
            desc_fr_with_fallback.fillna('')
        )
        # --- FIN MODIFICATION ---
        
        # 7. S'assurer que le répertoire de sortie existe
        os.makedirs(REPERTOIRE_SORTIE, exist_ok=True)

        # 8. Sauvegarder le fichier Odoo
        # La liste ci-dessous sert de vérification finale pour l'ordre
        colonnes_odoo_ordre = [
            'Name', 'Internal Reference', 'Brand', 'Can be Sold', 'Can be Purchased',
            'Is Publish', 'Product Category', 'Product Type', 'Sales Price', 
            'Detailed Price', 'Cost', 'Unit of Measure', 'Customer Taxes', 
            'Vendor Taxes', 'Invoicing Policy', 'Control Policy', 'Routes', 
            'Tracking', 'Variant Seller/Vendor', 'Variant Seller/Delivery Lead Time',
            'Variant Seller/Quantity', 'Variant Seller/Price', 'description_en', 
            'description_fr'
        ]
        
        # Réorganiser le DataFrame pour correspondre à la liste (sécurité)
        df_odoo = df_odoo.reindex(columns=colonnes_odoo_ordre)
        
        df_odoo.to_csv(output_file, index=False, encoding='utf-8')
        
        print("\n--- Succès ---")
        print(f"Fichier d'import Odoo sauvegardé ici : {output_file}")
        print(f"{len(df)} lignes lues au total.")
        print(f"{len(df_filtre)} lignes transformées et écrites pour Odoo.")

    except Exception as e:
        print(f"\n--- Erreur ---")
        print(f"Une erreur est survenue pendant le traitement : {e}")


# --- Exécution du script ---
if __name__ == "__main__":
    # Pour exécuter le script, il utilise la variable définie en haut
    filtrer_par_code(CODE_A_FILTRER_DEFAUT)