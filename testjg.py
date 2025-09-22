import requests
import json

# L'URL de l'API que vous voulez appeler
url = "https://sandbox-api.partscanada.com/api/v2/catalogues"

# Le jeton (token) Bearer pour l'authentification
# Il est préférable de le stocker dans une variable pour plus de clarté
bearer_token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJhdWQiOiIyODgiLCJqdGkiOiIzYWUwMTMxYjA2YmVmOTNkMmUyMDA4YjJkOTA5MDljYjU5MWJkZjg1NGExOGQ4NTQwMDJkZjcxMDZlNjIzYzQ5ZTFlOGZhYzQ2YjBlOGE0YiIsImlhdCI6MTc1Njg0MTU3My41Nzg1NywibmJmIjoxNzU2ODQxNTczLjU3ODU3MiwiZXhwIjo0OTEyNTE1MTczLjQ3NzI4Nywic3ViIjoiMjg4Iiwic2NvcGVzIjpbImludmVudG9yeS1saXN0IiwiaW52ZW50b3J5LXF1YW50aXRpZXMiLCJpbnZlbnRvcnktc3RvY2siLCJpbWFnZS1kb3dubG9hZCIsImNhdGFsb2d1ZS1saXN0IiwiY2F0YWxvZ3VlLWxpc3QtcGFydHMiLCJpbnZvaWNlLWxpc3QiLCJpbnZvaWNlLWRldGFpbHMiLCJpbnZvaWNlLWRvd25sb2FkIiwicHJvZHVjdC1mZWF0dXJlcy1kb3dubG9hZCIsInByb2R1Y3QtY29tbW9kaXR5LWNvZGVzLWRvd25sb2FkIiwic3RhdGVtZW50LWRvd25sb2FkIl19.6HKb_9a_Gihcvc3V1ZHfKDnio3InzPgPeryTGaFywIV5_61aSw_rmk6Ow69ymEhzdewisS_EfRH-9kL3Gecteb5HAyrJNfIfDAiTNGoAy_KRzoeGkhb5bQjKYkvMfAq0Q2J9GyBdXTpAt5Ji69BxMpDDhy1UhVYkLwolasZTwLb_s57HKcPgFyj7_uam7xP7K_2zydm3HdAw6tpkcuFwt-dY1U4DKCGC07ekcHBJ3CqCbfrdeqgBdrYsNNV32aRKOtCmwcv6LMccSA38MqNr-SN4BOIlqVk9FDrEtQiDMGCOgbi6e81P_ol1UOBu_Y-oeyjqoKlOWUAq9kBnlJqiDOe7XiwBgvx9UgIXWhlMRoZDvee342ioci_ASY8O_VOC2nHxWyGJf_gCk0qrjYSsvtUtKXXvJIr87G-GS7bJLOTTCIPB1Pf-zwTZbxUzgBq-0AfF_S59QciNss4djJ895Ty6BwkoBySsykjbOLhPqjv-lfpZ5dJhNzZPAd1G2mtmz6uMC-mDon83sJ4EtQPUCPqTGi35mAe3qZyw-Pk_F-zuf3esBIz55o8jfZW0KIyRwGvRbU7WsELKazSoT6PvGScMT_jL8VJit1X2nREFPgwUQKM9-ob1X8AV26HWjoixL2T4-yjHsFULxo3xZb6SJo6eB4SE968-mPuczS8b0JA"

# Les en-têtes (headers) de la requête, incluant l'autorisation
headers = {
    "Authorization": f"Bearer {bearer_token}"
}

# Envoyer la requête GET à l'API
response = requests.get(url, headers=headers)

# Vérifier si la requête a réussi (code de statut 200 OK)
if response.status_code == 200:
    # Afficher la réponse de l'API, probablement au format JSON
    print("Succès !")
    # Affiche le JSON joliment formaté
    print(json.dumps(response.json(), indent=4))
else:
    # Afficher le code d'erreur et le message si la requête a échoué
    print(f"Erreur lors de la requête : {response.status_code}")
    print(f"Réponse : {response.text}")