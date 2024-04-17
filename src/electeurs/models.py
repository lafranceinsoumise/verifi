from django.db import models


class TypeListe(models.TextChoices):
    PRINCIPALE = "LP", "Liste principale"
    EURO = "LCE", "Liste complémentaire européennes"
    MUNI = "LCM", "Liste complémentaire municipales"


class Civilite(models.TextChoices):
    MASC = "M", "M."
    FEM = "F", "Mme."


class Electeur(models.Model):
    code_com = models.CharField("Code INSEE commune", max_length=5)
    bureau = models.CharField("Bureau", max_length=10)
    num_electeur = models.IntegerField("Numéro dans la liste")
    type_liste = models.CharField(
        "Type de liste", max_length=3, choices=TypeListe.choices
    )

    sexe = models.CharField("Civilité", max_length=1, choices=Civilite.choices)
    nom = models.CharField("Nom de naissance", max_length=255)
    nom_usage = models.CharField("Nom d'usage", max_length=255, blank=True)
    prenoms = models.CharField("Prénoms", max_length=255)

    date_naissance = models.CharField("Date de naissance", max_length=10, blank=False)

    commune_naissance = models.CharField(
        "Ville de naissance", max_length=255, blank=True
    )
    pays_naissance = models.CharField("Pays de naissance", max_length=255, blank=True)
    nationalite = models.CharField("Nationalité", max_length=255, blank=True)

    num_voie = models.CharField("Numéro de voie", max_length=255, blank=True)
    voie = models.CharField("Nom de la voie", max_length=255, blank=True)
    comp1 = models.CharField("Complément d'adresse 1", max_length=255, blank=True)
    comp2 = models.CharField("Complément d'adresse 2", max_length=255, blank=True)
    lieu_dit = models.CharField("Lieu-dit", max_length=255, blank=True)
    code_postal = models.CharField("Code postal", max_length=255, blank=True)
    commune = models.CharField("Ville ou localité", max_length=255, blank=True)
    pays = models.CharField("Pays", max_length=255, blank=True)

    date_export = models.DateField("Date de l'export")

    def __str__(self):
        nom = self.nom.upper()
        if self.nom_usage and self.nom_usage.upper() != self.nom.upper():
            nom = f"{nom} ({self.nom_usage.upper()})"

        complement = self.date_naissance
        if self.type_liste != TypeListe.PRINCIPALE:
            complement = f"{complement}, {self.type_liste}"

        return f"{nom} {self.prenoms} ({complement})"

    def __repr__(self):
        return f"<Electeur(code_com={self.code_com!r}, date_naissance={self.date_naissance!r}, nom={self.nom!r}, prenoms={self.prenoms!r})>"

    def to_json(self):
        return {
            "nom": self.nom,
            "nom_usage": self.nom_usage,
            "prenoms": self.prenoms,
            "date_naissance": self.date_naissance,
            "type_liste": self.type_liste,
            "code_com": self.code_com,
            "bureau": self.bureau,
            "num_electeur": self.num_electeur,
        }

    class Meta:
        verbose_name = "électeur"
        constraints = [
            models.UniqueConstraint(
                fields=["code_com", "bureau", "type_liste", "num_electeur"],
                name="electeur_unique",
            )
        ]
