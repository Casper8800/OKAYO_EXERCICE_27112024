from catalogue import Catalogue
from facture import Facture, demander_facture

def afficher_menu_principal():
    print("Bienvenue dans le programme de gestion d'Okayo !")
    print("Vous êtes : ")
    print("1 - OKAYO")
    print("2 - Client")
    return input("Veuillez entrer le numéro correspondant à votre choix : ")

def menu_okayo(catalogue):
    while True:
        print("\nOptions OKAYO :")
        print("1 - Afficher le catalogue")
        print("2 - Modifier une valeur dans le catalogue")
        print("3 - Quitter")
        choix = input("Veuillez entrer le numéro correspondant à votre choix : ")

        if choix == "1":
            catalogue.afficher_catalogue()
        elif choix == "2":
            try:
                catalogue.afficher_catalogue()
                index = int(input("Entrez l'index du produit que vous souhaitez modifier : "))
                colonne = input("Entrez le nom de la colonne à modifier (Désignations, TVA, P.U HT, Quantités) : ")
                nouvelle_valeur = input("Entrez la nouvelle valeur : ")

                # Conversion de la nouvelle valeur si nécessaire
                if colonne in ["TVA", "P.U HT", "Quantités"]:
                    nouvelle_valeur = float(nouvelle_valeur)

                # Appliquer la modification
                catalogue.modifier_valeur(index, colonne, nouvelle_valeur)
                print("Valeur modifiée avec succès !")

                # Sauvegarder automatiquement après modification
                catalogue.sauvegarder_catalogue()
                catalogue.sauvegarder_pdf()
                print("Catalogue sauvegardé automatiquement en XLSX et PDF.")
                
            except (ValueError, KeyError):
                print("Erreur : index ou colonne invalide, veuillez réessayer.")
        elif choix == "3":
            print("Retour au menu principal.")
            break
        else:
            print("Choix non valide, veuillez réessayer.")

def menu_client(catalogue):
    print("\nBienvenue, cher client !")
    print("Vous pouvez maintenant choisir des produits pour générer une facture.")
    demander_facture(catalogue)

if __name__ == "__main__":
    # Charger le catalogue ou en créer un nouveau
    catalogue_okayo = Catalogue()

    # Afficher le menu principal
    choix_principal = afficher_menu_principal()
    if choix_principal == "1":
        menu_okayo(catalogue_okayo)
    elif choix_principal == "2":
        menu_client(catalogue_okayo)
    else:
        print("Choix non valide. Veuillez relancer le programme.")