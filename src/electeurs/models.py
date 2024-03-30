from django.db import models


class ListType(models.TextChoices):
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
        "Type de liste", max_length=3, choices=ListType.choices
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

    class Meta:
        verbose_name = "électeur"
        constraints = [
            models.UniqueConstraint(
                fields=["code_com", "bureau", "type_liste", "num_electeur"],
                name="electeur_unique",
            )
        ]


class EntreeRecherche(models.Model):
    code_com = models.CharField("Code INSEE commune", max_length=5)
    date_naissance = models.DateField("Date de naissance")
    nom = models.CharField("Nom de naissance", max_length=255)
    prenoms = models.CharField("Prénoms", max_length=255)

    electeur = models.ForeignKey(Electeur, on_delete=models.CASCADE)

    indexes = [
        models.Index(
            "code_com",
            "date_naissance",
            "nom",
            "prenoms",
            name="recherche_electeur",
        )
    ]
