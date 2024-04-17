from django.core.management import BaseCommand
from django.db import connection

from electeurs.models import TypeListe

INDEX_SQL = """
REFRESH MATERIALIZED VIEW CONCURRENTLY electeurs_recherche;
"""


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            "-l", "--liste", type=TypeListe, default=TypeListe.PRINCIPALE
        )

    def handle(self, liste, *args, **options):
        if liste != TypeListe.PRINCIPALE:
            listes = (TypeListe.PRINCIPALE, liste)
        else:
            listes = (TypeListe.PRINCIPALE,)

        with connection.cursor() as cursor:
            cursor.execute(INDEX_SQL, {"listes": listes})
