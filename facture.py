import pandas as pd
from fpdf import FPDF
import os
from catalogue import Catalogue


class Facture:
    def __init__(self, produits):
        """
        Initialize the Facture class with the selected products.

        :param produits: List of selected products, where each product is a list in the form:
                          [Désignation, TVA, P.U HT, Quantité]
        """
        # Create a DataFrame from the selected product data
        self.df = pd.DataFrame(produits, columns=["Désignation", "TVA", "P.U HT", "Quantité"])
        
        # Calculate the per-line totals
        self.df["Total HT"] = self.df["P.U HT"] * self.df["Quantité"]
        self.df["Total TTC"] = self.df["Total HT"] * (1 + self.df["TVA"] / 100)
        
        # Calculate overall totals
        self.total_tva = self.df["Total HT"].sum() * (self.df["TVA"].mean() / 100)
        self.total_ht = self.df["Total HT"].sum()
        self.total_ttc = self.df["Total TTC"].sum()
        self.total_quantite = self.df["Quantité"].sum()
        
        # Create a total row and append it to the DataFrame
        totals_row = {
            "Désignation": "TOTAL",
            "TVA": self.df["TVA"].sum(),
            "P.U HT": self.df["P.U HT"].sum(),
            "Quantité": self.total_quantite,
            "Total HT": self.total_ht,
            "Total TTC": self.total_ttc
        }
        
        self.df = pd.concat([self.df, pd.DataFrame([totals_row])], ignore_index=True)

    def sauvegarder_excel(self, fichier="FACTURE/facture.xlsx"):
        """ Save the invoice as an Excel file with totals at the bottom. """
        if not os.path.exists("FACTURE"):
            os.makedirs("FACTURE")
        self.df.to_excel(fichier, index=False)
        print(f"Invoice saved as Excel file: {fichier}")

    def sauvegarder_pdf(self, fichier_pdf="FACTURE/facture.pdf"):
        """ Save the invoice as a PDF file with totals at the bottom. """
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", "B", 12)

        # Title
        pdf.cell(200, 10, txt="Facture Okayo", ln=True, align='C')
        pdf.ln(10)

        # Table headers
        headers = ["Désignation", "TVA", "P.U HT", "Quantité", "Total HT", "Total TTC"]
        for header in headers:
            pdf.cell(30, 10, header, border=1, align="C")
        pdf.ln()

        # Table data
        pdf.set_font("Arial", "", 12)
        for _, row in self.df.iterrows():
            pdf.cell(30, 10, str(row["Désignation"]), border=1, align="C")
            pdf.cell(30, 10, f"{row['TVA']}%", border=1, align="C")  # Add percentage sign to TVA
            pdf.cell(30, 10, str(row["P.U HT"]), border=1, align="C")
            pdf.cell(30, 10, str(row["Quantité"]), border=1, align="C")
            pdf.cell(30, 10, str(row["Total HT"]), border=1, align="C")
            pdf.cell(30, 10, str(row["Total TTC"]), border=1, align="C")
            pdf.ln()

        # Save the PDF
        if not os.path.exists("FACTURE"):
            os.makedirs("FACTURE")
        pdf.output(fichier_pdf)
        print(f"Invoice saved as PDF file: {fichier_pdf}")


def demander_facture(catalogue_okayo):
    """Demander à l'utilisateur de choisir des produits et générer la facture"""
    produits_achetes = []

    while True:
        print("\nProduits disponibles dans le catalogue :")
        catalogue_okayo.afficher_catalogue()
        
        # Demander à l'utilisateur l'index du produit à acheter
        try:
            index = int(input("\nEntrez l'index du produit que vous voulez acheter (par exemple, 0, 1, 2) : "))
        except ValueError:
            print("Erreur : L'index doit être un nombre entier.")
            continue
        
        # Vérifier si l'index est valide et que le produit est en stock
        if index not in catalogue_okayo.catalogue_df.index:
            print("Erreur : Index invalide.")
            continue
        
        produit = catalogue_okayo.catalogue_df.loc[index]
        if produit["Quantités"] == -1:
            print("Ce produit n'est pas disponible à l'achat.")
            continue
        if produit["Quantités"] == 0:
            print("Ce produit est en rupture de stock.")
            continue
        
        # Demander la quantité à acheter
        try:
            quantite = int(input(f"Entrez la quantité pour '{produit['Désignations']}': "))
            if quantite > produit["Quantités"]:
                print("Erreur : Quantité demandée supérieure à la quantité en stock.")
                continue
        except ValueError:
            print("Erreur : La quantité doit être un nombre entier.")
            continue

        # Ajouter le produit au panier d'achat
        produits_achetes.append([produit['Désignations'], produit['TVA'], produit['P.U HT'], quantite])
        
        # Mise à jour du stock dans le catalogue
        catalogue_okayo.modifier_quantite(index, quantite)
        
        # Demander si l'utilisateur veut ajouter un autre produit
        reponse = input("\nVoulez-vous ajouter un autre produit ? (oui/non) : ")
        if reponse.lower() != "oui":
            confirmation = input("\nVoulez-vous confirmer vos achats et générer la facture ? (oui/non) : ")
            if confirmation.lower() == "oui":
                break
            else:
                print("\nAnnulation des achats.")
                return

    # Générer et sauvegarder la facture
    facture = Facture(produits_achetes)
    facture.sauvegarder_excel("FACTURE/facture.xlsx")
    facture.sauvegarder_pdf("FACTURE/facture.pdf")

    # Sauvegarder les modifications du catalogue
    catalogue_okayo.sauvegarder_catalogue()
    catalogue_okayo.sauvegarder_pdf()

    print("\nLa facture a été générée et le catalogue mis à jour.")