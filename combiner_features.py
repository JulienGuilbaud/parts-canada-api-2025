import pandas as pd
import os

def joindre_caracteristiques(series_de_textes):
    """
    Fonction d'aide pour agréger une série de textes en une seule chaîne
    formatée avec des puces.
    """
    textes_propres = [str(t) for t in series_de_textes if pd.notna(t) and str(t).strip()]
    if not textes_propres:
        return None
        
    return '\n• ' + '\n• '.join(textes_propres)

def lancer_combinaison_caracteristiques():
    """
    Fonction principale pour la logique de combinaison des caractéristiques.
    """
    print("Début de la combinaison des caractéristiques...")
    
    # --- 1. Définir les noms de fichiers (codés en dur) ---
    fichier_principal = r"INVENTAIRE-PARTS-CANADA\PartsCanadaCSV_8374000.csv"
    fichier_snow = r"CATALOGUES-snow\product_features_snow.csv"
    fichier_atv = r"CATALOGUES-atv-utv\product_features_atv-utv.csv"
    fichier_sortie = r"INVENTAIRE-PARTS-CANADA\PartsCanada_with_Features.csv"

    try:
        # --- 2. Charger les fichiers CSV ---
        print(f"Chargement de {fichier_principal}...")
        df_parts = pd.read_csv(fichier_principal)

        print(f"Chargement de {fichier_snow}...")
        df_snow = pd.read_csv(fichier_snow)

        print(f"Chargement de {fichier_atv}...")
        df_atv = pd.read_csv(fichier_atv)
        
        print("Fichiers chargés avec succès.")

        # --- 3. S'assurer que la colonne 'Part Number' est de type texte (str) ---
        print("Standardisation des types de données pour 'Part Number'...")
        df_parts['Part Number'] = df_parts['Part Number'].astype(str)
        df_snow['Part Number'] = df_snow['Part Number'].astype(str)
        df_atv['Part Number'] = df_atv['Part Number'].astype(str)

        # --- 4. Combiner les deux fichiers de caractéristiques ---
        print("Combinaison des fichiers de caractéristiques (snow et atv)...")
        df_features_all = pd.concat([df_snow, df_atv])

        df_features_all = df_features_all.drop_duplicates(subset=['Part Number', 'Feature Text'])
        df_features_all = df_features_all.dropna(subset=['Feature Text'])

        # --- 5. Agréger les caractéristiques ---
        print("Agrégation des caractéristiques par 'Part Number'...")
        
        features_agg = df_features_all.groupby('Part Number')['Feature Text'].apply(joindre_caracteristiques).reset_index()
        features_agg.rename(columns={'Feature Text': 'Features'}, inplace=True)
        
        print("Agrégation terminée.")

        # --- 6. Fusionner le fichier principal avec les caractéristiques agrégées ---
        print(f"Fusion de {fichier_principal} avec les nouvelles caractéristiques...")
        
        df_final = pd.merge(
            df_parts,
            features_agg,
            on='Part Number',
            how='left'
        )

        # --- 7. Sauvegarder le fichier résultant ---
        print(f"Sauvegarde du fichier final sous : {fichier_sortie}")
        df_final.to_csv(fichier_sortie, index=False)

        print("\nOpération de combinaison terminée avec succès !")
        print(f"Le fichier '{fichier_sortie}' a été créé.")
        print(f"Lignes dans le fichier original : {len(df_parts)}")
        print(f"Lignes dans le fichier final : {len(df_final)}")
        
        lignes_avec_features = df_final['Features'].notna().sum()
        print(f"Nombre de lignes avec caractéristiques ajoutées : {lignes_avec_features}")
        
    except FileNotFoundError as e:
        print(f"\n--- ERREUR (Combinaison) ---")
        print(f"Le fichier '{e.filename}' est introuvable.")
        print("Veuillez vous assurer que tous les fichiers CSV sont dans les bons dossiers.")
        # Lève l'exception pour être attrapée par le bloc principal
        raise e
    except Exception as e:
        print(f"\n--- ERREUR INATTENDUE (Combinaison) ---")
        print(f"Une erreur est survenue : {e}")
        # Lève l'exception pour être attrapée par le bloc principal
        raise e

# Ce bloc permet de tester ce module spécifiquement
if __name__ == "__main__":
    print("Test du module de combinaison en mode autonome...")
    try:
        lancer_combinaison_caracteristiques()
        print("Test de combinaison réussi.")
    except Exception as e:
        print(f"Test de combinaison a échoué : {e}")