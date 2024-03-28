from django.contrib.postgres.lookups import Unaccent
from django.db import models
from django.db.models.functions import Lower, Upper


class ListType(models.TextChoices):
    PRINCIPALE = "LP", "Liste principale"
    EURO = "LCE", "Liste complémentaire européennes"
    MUNI = "LCM", "Liste complémentaire municipales"


class Civilite(models.TextChoices):
    MASC = "M", "M."
    FEM = "F", "Mme."


class Electeur(models.Model):
    commune = models.CharField("Code INSEE commune", max_length=5)
    bureau = models.CharField("Bureau", max_length=4)
    numero = models.IntegerField("Numéro dans la liste")
    type_liste = models.CharField(
        "Type de liste", max_length=3, choices=ListType.choices
    )

    sexe = models.CharField("Civilité", max_length=1, choices=Civilite.choices)
    nom = models.CharField("Nom de naissance", max_length=255)
    nom_usage = models.CharField("Nom d'usage", max_length=255, blank=True)
    prenoms = models.CharField("Prénoms", max_length=255)

    date_naissance = models.DateField("Date de naissance")
    commune_naissance = models.CharField(
        "Ville de naissance", max_length=255, blank=True
    )
    pays_naissance = models.CharField("Pays de naissance", max_length=255, blank=True)
    nationalite = models.CharField("Nationalité", max_length=255, blank=True)

    numero_voie = models.CharField("Numéro de voie", max_length=255, blank=True)
    voie = models.CharField("Nom de la voie", max_length=255, blank=True)
    comp1 = models.CharField("Complément d'adresse 1", max_length=255, blank=True)
    comp2 = models.CharField("Complément d'adresse 2", max_length=255, blank=True)
    lieu_dit = models.CharField("Lieu-dit", max_length=255, blank=True)
    code_postal = models.CharField("Code postal", max_length=255, blank=True)
    ville = models.CharField("Ville ou localité", max_length=255, blank=True)
    pays = models.CharField("Pays", max_length=255, blank=True)

    date_export = models.DateField("Date de l'export")

    class Meta:
        verbose_name = "électeur"
        constraints = [
            models.UniqueConstraint(
                fields=["commune", "bureau", "numero"], name="electeur_unique"
            )
        ]

        indexes = [
            models.Index(
                "commune",
                "date_naissance",
                Upper(Unaccent("nom")),
                name="recherche_nom_legal",
            ),
            models.Index(
                "commune",
                "date_naissance",
                Upper(Unaccent("nom_usage")),
                name="recherche_nom_usage",
            ),
        ]
