# Generated by Django 5.0.3 on 2024-03-28 16:01

import django.contrib.postgres.lookups
import django.db.models.functions.text
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Electeur",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "commune",
                    models.CharField(max_length=5, verbose_name="Code INSEE commune"),
                ),
                ("bureau", models.CharField(max_length=4, verbose_name="Bureau")),
                ("numero", models.IntegerField(verbose_name="Numéro dans la liste")),
                (
                    "type_liste",
                    models.CharField(
                        choices=[
                            ("LP", "Liste principale"),
                            ("LCE", "Liste complémentaire européennes"),
                            ("LCM", "Liste complémentaire municipales"),
                        ],
                        max_length=3,
                        verbose_name="Type de liste",
                    ),
                ),
                (
                    "sexe",
                    models.CharField(
                        blank=True,
                        choices=[("M", "M."), ("F", "Mme.")],
                        max_length=1,
                        verbose_name="Civilité",
                    ),
                ),
                (
                    "nom",
                    models.CharField(max_length=255, verbose_name="Nom de naissance"),
                ),
                (
                    "nom_usage",
                    models.CharField(
                        blank=True, max_length=255, verbose_name="Nom d'usage"
                    ),
                ),
                ("prenoms", models.CharField(max_length=255, verbose_name="Prénoms")),
                (
                    "date_naissance",
                    models.DateField(
                        blank=True, null=True, verbose_name="Date de naissance"
                    ),
                ),
                (
                    "commune_naissance",
                    models.CharField(
                        blank=True, max_length=255, verbose_name="Ville de naissance"
                    ),
                ),
                (
                    "pays_naissance",
                    models.CharField(
                        blank=True, max_length=255, verbose_name="Pays de naissance"
                    ),
                ),
                (
                    "nationalite",
                    models.CharField(
                        blank=True, max_length=255, verbose_name="Nationalité"
                    ),
                ),
                (
                    "numero_voie",
                    models.CharField(
                        blank=True, max_length=255, verbose_name="Numéro de voie"
                    ),
                ),
                (
                    "voie",
                    models.CharField(
                        blank=True, max_length=255, verbose_name="Nom de la voie"
                    ),
                ),
                (
                    "comp1",
                    models.CharField(
                        blank=True,
                        max_length=255,
                        verbose_name="Complément d'adresse 1",
                    ),
                ),
                (
                    "comp2",
                    models.CharField(
                        blank=True,
                        max_length=255,
                        verbose_name="Complément d'adresse 2",
                    ),
                ),
                (
                    "lieu_dit",
                    models.CharField(
                        blank=True, max_length=255, verbose_name="Lieu-dit"
                    ),
                ),
                (
                    "code_postal",
                    models.CharField(
                        blank=True, max_length=255, verbose_name="Code postal"
                    ),
                ),
                (
                    "ville",
                    models.CharField(
                        blank=True, max_length=255, verbose_name="Ville ou localité"
                    ),
                ),
                (
                    "pays",
                    models.CharField(blank=True, max_length=255, verbose_name="Pays"),
                ),
                ("date_export", models.DateField(verbose_name="Date de l'export")),
            ],
            options={
                "verbose_name": "électeur",
                "indexes": [
                    models.Index(
                        models.F("commune"),
                        models.F("date_naissance"),
                        django.db.models.functions.text.Upper(
                            django.contrib.postgres.lookups.Unaccent("nom")
                        ),
                        name="recherche_nom_legal",
                    ),
                    models.Index(
                        models.F("commune"),
                        models.F("date_naissance"),
                        django.db.models.functions.text.Upper(
                            django.contrib.postgres.lookups.Unaccent("nom_usage")
                        ),
                        name="recherche_nom_usage",
                    ),
                ],
            },
        ),
        migrations.AddConstraint(
            model_name="electeur",
            constraint=models.UniqueConstraint(
                fields=("commune", "bureau", "numero"), name="electeur_unique"
            ),
        ),
    ]
