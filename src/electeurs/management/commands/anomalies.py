import csv
from importlib.resources import files

import pandas as pd
from django.core.management import BaseCommand
from django.db.models import F, Count
from django.db.models.functions import Substr

from electeurs.models import Electeur


RED = "91"
GREEN = "92"

COLORED_TEXT = "\033[{color}m{text}\033[0m"


class Command(BaseCommand):
    def handle(self, *args, **options):
        with files("electeurs").joinpath("communes.csv").open("r") as fd:
            reader = csv.DictReader(fd)
            communes = list(reader)

        with files("electeurs").joinpath("departements.csv").open("r") as fd:
            reader = csv.DictReader(fd)
            inscrits_departements = {l["code_dep"]: int(l["inscrits"]) for l in reader}

        deps = list(
            Electeur.objects.annotate(departement=Substr(F("code_com"), 1, 2))
            .order_by("departement")
            .values("departement")
            .annotate(nb=Count("id"))
            .values_list("departement", "nb")
        )

        print(f"{len(deps)} départements importés.\n")

        print("Comparaison des nombres d'électeurs par département (base 2022)")
        for d, nb in deps:
            nb_2022 = inscrits_departements[d]
            evolution = (nb - nb_2022) / nb_2022
            if evolution < -0.05:
                evolution = COLORED_TEXT.format(color=RED, text=f"{evolution:.1%}")
            elif evolution > 0.1:
                evolution = COLORED_TEXT.format(color=GREEN, text=f"{evolution:.1%}")
            else:
                evolution = f"{evolution:.1%}"

            print(f"{d}: {nb} - {evolution}")

        print("")

        print("Communes manquantes")
        for d, _ in deps:
            communes_avec_electeur = set(
                Electeur.objects.filter(code_com__startswith=d)
                .values_list("code_com", flat=True)
                .distinct()
            )

            communes_manquantes = [
                c
                for c in communes
                if c["code_com"].startswith(d)
                and c["code_com"] not in communes_avec_electeur
            ]

            if communes_manquantes:
                print(f"{d}: {len(communes_manquantes)}")
                if len(communes_manquantes) < 6:
                    print(", ".join(c["nom"] for c in communes_manquantes))
