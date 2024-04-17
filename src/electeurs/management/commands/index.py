from django.core.management import BaseCommand
from django.db import connection

from electeurs.models import TypeListe

INDEX_SQL = """
INSERT INTO electeurs_entreerecherche (code_com, date_naissance, nom, prenoms, electeur_id, nom_usage)
SELECT
  code_com,
  date_naissance,
  UPPER(UNACCENT(nom)),
  UPPER(UNACCENT(prenoms)),
  id,
  FALSE
FROM electeurs_electeur
WHERE type_liste IN %(listes)s
ON CONFLICT (electeur_id, nom_usage)
DO UPDATE SET
  code_com = excluded.code_com,
  date_naissance = excluded.date_naissance,
  nom = excluded.nom,
  prenoms = excluded.prenoms;

INSERT INTO electeurs_entreerecherche (code_com, date_naissance, nom, prenoms, electeur_id, nom_usage)
SELECT
  code_com,
  date_naissance,
  UPPER(UNACCENT(nom_usage)),
  UPPER(UNACCENT(prenoms)),
  id,
  TRUE
FROM electeurs_electeur
WHERE type_liste IN %(listes)s
  AND nom_usage != '' AND UPPER(UNACCENT(nom_usage)) != UPPER(UNACCENT(nom))
ON CONFLICT (electeur_id, nom_usage)
DO UPDATE SET
  code_com = excluded.code_com,
  date_naissance = excluded.date_naissance,
  nom = excluded.nom,
  prenoms = excluded.prenoms;

DELETE FROM electeurs_entreerecherche entree
USING electeurs_electeur electeur
WHERE electeur.id = entree.electeur_id 
 AND (
   electeur.type_liste NOT IN %(listes)s
   OR (
     entree.nom_usage
     AND (
       electeur.nom_usage = '' 
       OR UPPER(UNACCENT(electeur.nom_usage)) = UPPER(UNACCENT(electeur.nom))
     )
   )  
 );
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
