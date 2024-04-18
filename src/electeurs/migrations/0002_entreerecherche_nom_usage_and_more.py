# Generated by Django 5.0.3 on 2024-04-15 15:46

from django.db import migrations

FORWARD_SQL = """
CREATE MATERIALIZED VIEW electeurs_recherche AS (
  SELECT
    code_com,
    date_naissance,
    UPPER(UNACCENT(nom)) AS nom,
    UPPER(UNACCENT(prenoms)) AS prenoms,
    id as electeur_id,
    FALSE AS usage
  FROM electeurs_electeur

  UNION ALL

  SELECT
    code_com,
    date_naissance,
    UPPER(UNACCENT(nom_usage)),
    UPPER(UNACCENT(prenoms)),
    id as electeur_id,
    TRUE AS usage
  FROM electeurs_electeur
  WHERE nom_usage != '' AND UPPER(UNACCENT(nom_usage)) != UPPER(UNACCENT(nom))
);

CREATE INDEX electeurs_recherche_index ON electeurs_recherche (code_com, date_naissance, nom, prenoms);
CREATE UNIQUE INDEX electeurs_recherche_unique ON electeurs_recherche (electeur_id, usage);
"""

REVERSE_SQL = """
DROP MATERIALIZED VIEW electeurs_recherche;
"""


class Migration(migrations.Migration):
    dependencies = [
        ("electeurs", "0001_initial"),
    ]

    operations = [
        migrations.RunSQL(sql=FORWARD_SQL, reverse_sql=REVERSE_SQL),
    ]