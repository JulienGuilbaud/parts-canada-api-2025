import requests
import json
import csv
import os
import re
import zipfile
import io
import pandas as pd
from urllib.parse import urljoin
from dotenv import load_dotenv

# --- Configuration ---
# Charge les variables d'environnement à partir du fichier .env
load_dotenv()

# Récupère la clé d'API depuis les variables d'environnement.
# Le script cherchera la variable PARTS_CANADA_API_KEY dans votre fichier .env
API_KEY = os.environ.get('PARTS_CANADA_API_KEY')

# Spécification OpenAPI intégrée pour la simplicité
# La version Production a été retirée pour se concentrer sur le Sandbox.
OPENAPI_SPEC = {
  "servers": [
    { "url": "https://sandbox-api.partscanada.com/api/v2", "description": "Sandbox (Développement)" }
  ],
  "paths": {
    "/catalogues": { "get": { "summary": "Get list of catalogues", "operationId": "catalogue-list", "tags": ["Catalogues"] } },
    "/catalogues/{name}": { "get": { "summary": "Get details for a catalogue", "operationId": "catalogue-details", "tags": ["Catalogues"], "parameters": [{ "name": "name", "in": "path", "required": True, "schema": { "type": "string" } }] } },
    "/catalogues/{name}/parts": { "get": { "summary": "Download parts from a catalogue", "operationId": "catalogue-parts", "tags": ["Catalogues"], "parameters": [{ "name": "name", "in": "path", "required": True, "schema": { "type": "string" } }] } },
    "/images/{part_number}/download": { "get": { "summary": "Download images", "operationId": "image-download", "tags": ["Images"], "parameters": [{ "name": "part_number", "in": "path", "required": True, "schema": { "type": "string" } }] } },
    "/inventory": { "get": { "summary": "Download inventory file", "operationId": "inventory-download", "tags": ["Inventory"] } },
    "/inventory/extended": { "get": { "summary": "Download extended inventory file", "operationId": "inventory-extended-download", "tags": ["Inventory"] } },
    "/inventory/quantities": { "get": { "summary": "Download inventory quantity file", "operationId": "inventory-quantities-download", "tags": ["Inventory"] } },
    "/inventory/{part_number}/stock": { "get": { "summary": "Get inventory stock information", "operationId": "inventory-stock", "tags": ["Inventory"], "parameters": [{ "name": "part_number", "in": "path", "required": True, "schema": { "type": "string" } }] } },
    "/products/commodity-codes/download": { "get": { "summary": "Download commodity code file", "operationId": "product-commodity-codes-download", "tags": ["Products"] } },
    "/products/features/{catalogue}/download": { "get": { "summary": "Download product features file", "operationId": "product-features-download", "tags": ["Products"], "parameters": [{ "name": "catalogue", "in": "path", "required": True, "schema": { "type": "string", "enum": ["atv-utv", "bicycle", "fatbook", "helmet-and-apparel", "offroad", "oldbook", "snow", "street", "tire-and-service"] } }, { "name": "start_date", "in": "query", "required": False, "schema": { "type": "string" } }] } },
    "/statements/{date}/{account}/download": { "get": { "summary": "Download statement", "operationId": "statement-download", "tags": ["Statements"], "parameters": [{ "name": "date", "in": "path", "required": True, "schema": { "type": "string" } }, { "name": "account", "in": "path", "required": True, "schema": { "type": "string" } }] } },
    "/invoices": { "get": { "summary": "Get invoices", "operationId": "invoice-list", "tags": ["Invoices"], "parameters": [{ "name": "start_date", "in": "query", "required": True, "schema": { "type": "string" } }, { "name": "end_date", "in": "query", "required": True, "schema": { "type": "string" } }] } },
    "/invoices/{invoice_number}": { "get": { "summary": "Get invoice details", "operationId": "invoice-details", "tags": ["Invoices"], "parameters": [{ "name": "invoice_number", "in": "path", "required": True, "schema": { "type": "string" } }] } },
    "/invoices/{invoice_number}/download": { "get": { "summary": "Download invoice", "operationId": "invoice-download", "tags": ["Invoices"], "parameters": [{ "name": "invoice_number", "in": "path", "required": True, "schema": { "type": "string" } }] } }
  }
}

# --- Fonctions Utilitaires ---

def print_colored(text, color):
    colors = {"header": "\033[95m", "blue": "\033[94m", "green": "\033[92m", "warning": "\033[93m", "fail": "\033[91m", "endc": "\033[0m", "bold": "\033[1m"}
    print(f"{colors.get(color, '')}{text}{colors['endc']}")

def select_from_list(options, prompt):
    for i, option in enumerate(options):
        print(f"  {i + 1}. {option}")
    while True:
        try:
            choice = int(input(prompt))
            if 1 <= choice <= len(options):
                return options[choice - 1]
        except (ValueError, IndexError):
            print_colored("Choix invalide. Veuillez réessayer.", "fail")

def get_api_response(base_url, path, params={}):
    """Effectue un appel API et retourne l'objet réponse complet."""
    if not API_KEY:
        print_colored("Erreur : La clé d'API (PARTS_CANADA_API_KEY) n'est pas définie.", "fail")
        print_colored("Veuillez la définir dans votre fichier .env.", "warning")
        return None
    headers = {'Authorization': f'Bearer {API_KEY}', 'Accept': 'application/json, application/octet-stream'}
    path_params = {k: v for k, v in params.items() if f"{{{k}}}" in path}
    query_params = {k: v for k, v in params.items() if f"{{{k}}}" not in path}
    for name, value in path_params.items():
        path = path.replace(f"{{{name}}}", str(value))
    url = urljoin(base_url, path)
    print_colored(f"\n> Appel de l'API : {url}", "blue")
    try:
        response = requests.get(url, headers=headers, params=query_params, timeout=60, stream=True)
        response.raise_for_status()
        return response
    except requests.exceptions.RequestException as e:
        print_colored(f"Erreur lors de la requête API : {e}", "fail")
        return None

def download_and_extract_csv(response):
    """Télécharge un ZIP en mémoire, l'extrait et retourne un DataFrame Pandas.
    Gère également les réponses qui sont du texte brut ou un CSV direct."""
    content_type = response.headers.get('Content-Type', '').lower()

    # Gère les réponses en texte brut (par exemple, "Pas de mises à jour")
    if 'text/plain' in content_type:
        print_colored(f"  - Réponse texte reçue, aucun fichier à traiter : {response.text}", "warning")
        return None

    # Gère les réponses d'erreur JSON potentielles qui sont arrivées avec un statut 200 OK
    if 'application/json' in content_type:
        try:
            print_colored(f"  - Réponse JSON inattendue reçue : {response.json()}", "fail")
        except json.JSONDecodeError:
            print_colored(f"  - Réponse JSON inattendue (et invalide) reçue : {response.text}", "fail")
        return None

    # Essaye de traiter comme un fichier ZIP en premier, car c'est le cas le plus courant.
    try:
        with zipfile.ZipFile(io.BytesIO(response.content)) as z:
            csv_files = [name for name in z.namelist() if name.lower().endswith('.csv')]
            if not csv_files:
                print_colored("  - Erreur : Aucun fichier CSV trouvé dans l'archive ZIP.", "fail")
                return None
            csv_filename = csv_files[0]
            print(f"  - Extraction du fichier CSV : {csv_filename}")
            with z.open(csv_filename) as f:
                return pd.read_csv(f, low_memory=False)
    except zipfile.BadZipFile:
        # Si ce n'est pas un fichier zip, il pourrait s'agir d'un CSV brut.
        print_colored("  - La réponse n'est pas un fichier ZIP. Tentative de lecture en tant que CSV direct...", "warning")
        try:
            # Il faut utiliser un nouvel objet BytesIO car le précédent a pu être partiellement lu.
            return pd.read_csv(io.BytesIO(response.content), low_memory=False)
        except Exception as e:
            print_colored(f"  - Échec de la lecture en tant que CSV direct : {e}", "fail")
            print_colored(f"  - Contenu de la réponse (premiers 200 caractères) : {response.text[:200]}", "warning")
            return None
    except (IndexError, pd.errors.ParserError) as e:
        print_colored(f"Erreur lors du traitement du fichier ZIP/CSV : {e}", "fail")
        return None

# --- Fonctions de Transformation pour Odoo ---

def transform_merged_data_to_odoo_csv(df, selected_category):
    """Transforme le DataFrame fusionné en un format prêt pour Odoo."""
    print_colored("\nTransformation des données fusionnées pour Odoo...", "bold")
    headers = ['id', 'name', 'default_code', 'description_sale', 'type', 'categ_id/id', 'list_price', 'standard_price']
    rows = []
    
    # Créer un ID externe pour la catégorie Odoo
    safe_category_name = re.sub(r'[^a-zA-Z0-9_]', '_', selected_category).lower()
    odoo_category_id = f"__export__.product_category_partscanada_{safe_category_name}"

    for _, row in df.iterrows():
        part_number = str(row.get('Part Number', ''))
        if not part_number:
            continue
            
        safe_part_num = re.sub(r'[^a-zA-Z0-9_]', '_', part_number)
        external_id = f"__export__.product_template_partscanada_{safe_part_num}"
        
        rows.append({
            'id': external_id,
            'name': row.get('Description EN', part_number),
            'default_code': part_number,
            'description_sale': row.get('Feature Text', ''),
            'type': 'product',
            'categ_id/id': odoo_category_id, # Assigner la catégorie Odoo
            'list_price': row.get('MSRP Latest', ''),
            'standard_price': row.get('Dealer Price', ''),
        })
    return headers, rows

# --- Flux de Travail Principal ---

def run_full_import_workflow(base_url):
    """Exécute le processus complet d'importation des produits."""
    print_colored("\n--- Lancement du Flux d'Importation Complet des Produits ---", "header")

    # 1. Télécharger les catégories (Commodity Codes)
    print_colored("\nÉtape 1: Téléchargement des catégories de produits...", "bold")
    commodity_response = get_api_response(base_url, "/products/commodity-codes/download")
    if not commodity_response: return
    commodity_df = download_and_extract_csv(commodity_response)
    if commodity_df is None: return
    
    # Assumons que la colonne de catégorie s'appelle 'Commodity EN' ou similaire.
    # Il faut trouver la bonne colonne.
    category_column = next((col for col in commodity_df.columns if 'Commodity' in col), None)
    if not category_column:
        print_colored("Impossible de trouver la colonne des catégories dans le fichier.", "fail")
        return
        
    available_categories = sorted(commodity_df[category_column].dropna().unique())
    print_colored(f"  - {len(available_categories)} catégories trouvées.", "green")
    
    # 2. Sélectionner une catégorie
    print_colored("\nÉtape 2: Sélection d'une catégorie à extraire...", "bold")
    selected_category = select_from_list(available_categories, "Votre choix : ")
    
    # Filtrer les numéros de pièce pour la catégorie choisie
    part_numbers_in_category = commodity_df[commodity_df[category_column] == selected_category]['Part Number'].astype(str).tolist()
    print_colored(f"  - {len(part_numbers_in_category)} produits trouvés dans la catégorie '{selected_category}'.", "green")

    # 3. Télécharger l'inventaire complet
    print_colored("\nÉtape 3: Téléchargement de l'inventaire complet...", "bold")
    inventory_response = get_api_response(base_url, "/inventory")
    if not inventory_response: return
    inventory_df = download_and_extract_csv(inventory_response)
    if inventory_df is None: return
    inventory_df['Part Number'] = inventory_df['Part Number'].astype(str)
    
    # 4. Filtrer l'inventaire
    print_colored("\nÉtape 4: Filtrage de l'inventaire par catégorie...", "bold")
    filtered_inventory_df = inventory_df[inventory_df['Part Number'].isin(part_numbers_in_category)]
    print_colored(f"  - {len(filtered_inventory_df)} produits de l'inventaire correspondent à la catégorie.", "green")

    # 5. Télécharger les descriptions (features)
    print_colored("\nÉtape 5: Téléchargement des descriptions de produits...", "bold")
    catalogue_enum = OPENAPI_SPEC['paths']['/products/features/{catalogue}/download']['get']['parameters'][0]['schema']['enum']
    selected_catalogue = select_from_list(catalogue_enum, "Pour quel catalogue télécharger les descriptions ? ")
    
    features_response = get_api_response(base_url, f"/products/features/{selected_catalogue}/download")
    if not features_response: return
    features_df = download_and_extract_csv(features_response)
    if features_df is None: return
    features_df['Part Number'] = features_df['Part Number'].astype(str)
    print_colored(f"  - {len(features_df)} descriptions trouvées pour le catalogue '{selected_catalogue}'.", "green")

    # 6. Fusionner les données filtrées
    print_colored("\nÉtape 6: Fusion des données d'inventaire filtrées et des descriptions...", "bold")
    merged_df = pd.merge(filtered_inventory_df, features_df[['Part Number', 'Feature Text']], on='Part Number', how='left')
    print_colored(f"  - Fusion terminée. Le jeu de données final contient {len(merged_df)} produits.", "green")

    # 7. Récupérer les liens des archives d'images
    print_colored("\nÉtape 7: Récupération des liens d'archives d'images...", "bold")
    catalogues_response = get_api_response(base_url, "/catalogues")
    if catalogues_response:
        catalogues_data = catalogues_response.json()
        print("  - Liens pour télécharger les archives d'images complètes :")
        for cat in catalogues_data:
            print_colored(f"    - {cat.get('title_en', 'N/A')} ({cat.get('year', 'N/A')}): {cat.get('archive', 'Lien non disponible')}", "blue")

    # 8. Transformer et Sauvegarder
    headers, rows = transform_merged_data_to_odoo_csv(merged_df, selected_category)
    if rows:
        safe_filename = re.sub(r'[^a-zA-Z0-9_]', '_', selected_category)
        filename = f"odoo_import_produits_{safe_filename}.csv"
        print_colored(f"\nÉtape 8: Sauvegarde des données transformées dans '{filename}'...", "bold")
        save_to_csv(filename, headers, rows)

def save_to_csv(filename, headers, rows):
    if not rows:
        print_colored("Aucune donnée à sauvegarder.", "warning")
        return
    try:
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=headers)
            writer.writeheader()
            writer.writerows(rows)
        print_colored(f"Données sauvegardées avec succès dans '{filename}'", "green")
    except IOError as e:
        print_colored(f"Erreur lors de la sauvegarde du fichier CSV : {e}", "fail")

def main():
    """Fonction principale du script interactif."""
    print_colored("--- Outil ETL Parts Canada vers Odoo (Avancé) ---", "header")
    
    base_url = OPENAPI_SPEC['servers'][0]['url']
    print_colored(f"\nUtilisation de l'environnement Sandbox : {base_url}", "bold")
    
    run_full_import_workflow(base_url)

    print_colored("\n--- Opération terminée ---", "header")

if __name__ == "__main__":
    main()
