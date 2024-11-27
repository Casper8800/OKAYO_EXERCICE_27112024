import pandas as pd
from fpdf import FPDF
import sys

class Catalogue:
    def __init__(self, fichier="CATALOGUE/catalogue.xlsx"):
        """Tentative de charger un fichier Excel s'il existe"""
        try:
            self.catalogue_df = pd.read_excel(fichier, index_col=0)
        except FileNotFoundError:
            # Si le fichier n'existe pas, créer un catalogue initial sans "Fréquence d'achat"
            self.catalogue_df = pd.DataFrame(columns=["Désignations", "TVA", "P.U HT", "Quantités"])
            self.catalogue_df.loc[0] = ["Produit A", 20, 100, 50]
            self.catalogue_df.loc[1] = ["Produit B", 5, 200, 30]
            self.catalogue_df.loc[2] = ["Produit C", 10, 150, -1]  # Quantité -1 pour test "N/A"
        
        self.fichier = fichier  # Enregistrer le nom du fichier pour la sauvegarde
    
    def afficher_catalogue(self):
        """Afficher le catalogue avec 'N/A' pour les quantités -1 et 'Rupture de stock' pour 0"""
        catalogue_affichage = self.catalogue_df.copy()
        catalogue_affichage["Quantités"] = catalogue_affichage["Quantités"].apply(
            lambda q: "N/A" if q == -1 else ("Rupture de stock" if q == 0 else q)
        )
        print(catalogue_affichage.to_string(index=True))
    
    def modifier_valeur(self, index, colonne, nouvelle_valeur):
        """Modifier une valeur dans le catalogue"""
        if colonne in self.catalogue_df.columns:
            self.catalogue_df.at[index, colonne] = nouvelle_valeur
        else:
            print(f"Erreur : La colonne '{colonne}' n'existe pas.")
    
    def modifier_quantite(self, index, quantite_vendue):
        """Décrémente la quantité d'un produit après un achat si stock suffisant."""
        if index in self.catalogue_df.index:
            quantite_disponible = self.catalogue_df.at[index, "Quantités"]

            if quantite_disponible == -1:
                print("Ce produit n'est pas disponible à l'achat.")
                return
            
            if quantite_vendue <= quantite_disponible:
                nouvelle_quantite = quantite_disponible - quantite_vendue
                self.catalogue_df.at[index, "Quantités"] = nouvelle_quantite
                print(f"Quantité de '{self.catalogue_df.at[index, 'Désignations']}' mise à jour : {nouvelle_quantite} restantes.")
            else:
                print(f"Erreur : Quantité demandée ({quantite_vendue}) est supérieure à la quantité disponible ({quantite_disponible}) en stock.")
        else:
            print("Erreur : Index invalide.")
    
    def sauvegarder_catalogue(self):
        """Sauvegarder le catalogue dans un fichier Excel dans le dossier CATALOGUE"""
        self.catalogue_df.to_excel("CATALOGUE/catalogue.xlsx")
        print("Catalogue sauvegardé dans 'CATALOGUE/catalogue.xlsx'")
    
    def sauvegarder_pdf(self, fichier_pdf="CATALOGUE/catalogue.pdf"):
        """Sauvegarder le catalogue sous forme de PDF dans le dossier CATALOGUE"""
        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()
        
        # Ajouter un titre
        pdf.set_font('Arial', 'B', 16)
        pdf.cell(200, 10, txt="Catalogue Offre Okayo ", ln=True, align='C')

        # Ajouter les entêtes de colonnes
        pdf.ln(10)  # Saut de ligne
        pdf.set_font('Arial', 'B', 12)
        headers = self.catalogue_df.columns.tolist()
        for header in headers:
            pdf.cell(40, 10, txt=header, border=1, align='C')
        pdf.ln()

        # Ajouter les données du catalogue avec gestion des quantités spéciales
        pdf.set_font('Arial', '', 12)
        for index, row in self.catalogue_df.iterrows():
            quantite = "N/A" if row["Quantités"] == -1 else ("Rupture de stock" if row["Quantités"] == 0 else row["Quantités"])
            for value in [row["Désignations"], row["TVA"], row["P.U HT"], quantite]:
                pdf.cell(40, 10, txt=str(value), border=1, align='C')
            pdf.ln()

        # Sauvegarder le PDF
        pdf.output(fichier_pdf)
        print(f"Catalogue sauvegardé en PDF sous le nom : {fichier_pdf}")
