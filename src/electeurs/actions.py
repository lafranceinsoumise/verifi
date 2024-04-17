from enum import StrEnum

from django.contrib.postgres.lookups import Unaccent
from django.db.models.functions import Upper

from electeurs.models import Electeur, TypeListe


RECHERCHE_SQL = """
SELECT e.*
FROM electeurs_electeur e
JOIN electeurs_recherche r ON e.id = r.electeur_id
WHERE
  r.code_com = %(code_com)s
  AND r.date_naissance = %(date_naissance)s
  AND r.nom = UPPER(UNACCENT(%(nom)s))
  AND r.prenoms = UPPER(UNACCENT(%(prenoms)s))
  AND e.type_liste IN %(type_liste)s
LIMIT 1
"""


class TypeElection(StrEnum):
    europeennes = "europeennes"
    municipales = "municipales"
    autre = "autre"


ELECTIONS = {
    TypeElection.autre: (TypeListe.PRINCIPALE,),
    TypeElection.europeennes: (TypeListe.PRINCIPALE, TypeListe.EURO),
    TypeElection.municipales: (TypeListe.PRINCIPALE, TypeListe.MUNI),
}


def Normaliser(f):
    return Upper(Unaccent(f))


def verifier_electeur(code_com, date_naissance, nom, prenoms, election: TypeElection):
    raw = Electeur.objects.raw(
        RECHERCHE_SQL,
        {
            "code_com": code_com,
            "date_naissance": date_naissance,
            "nom": nom,
            "prenoms": prenoms,
            "type_liste": ELECTIONS[election],
        },
    )
    return raw and raw[0]
