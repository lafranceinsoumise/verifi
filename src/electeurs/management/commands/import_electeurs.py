import contextlib
import csv
from itertools import chain, islice
from pathlib import Path

from django.core.management import BaseCommand
from django.db import connection
from psycopg2.sql import SQL, Identifier
from tqdm import tqdm

REQUIRED_FIELDS = {
    "code_com",
    "type_liste",
    "nom",
    "nom_usage",
    "prénoms",
    "sexe",
    "date_naissance",
    "bureau",
    "num_electeur",
    "date_export",
}

UNIQUE_FIELDS = ["code_com", "bureau", "type_liste", "num_electeur"]

COPY_SQL = SQL(
    """COPY {table} ({columns}) FROM STDIN WITH NULL AS '\\N' CSV QUOTE AS '"';"""
)


CREATE_TEMP_TABLE_SQL = SQL(
    """
    CREATE TEMPORARY TABLE {temp_table} AS
    SELECT {columns} FROM {reference_table} LIMIT 0;
    """
)
DROP_TEMPORARY_TABLE_SQL = SQL(
    """
    DROP TABLE IF EXISTS {temp_table};
    """
)


COPY_FROM_TEMP_TABLE = SQL(
    """
    INSERT INTO {table} ({column_list})
    SELECT {select_list}
    FROM {temp_table}
    ON CONFLICT({id_columns}) DO UPDATE SET {setters};
    """
)


@contextlib.contextmanager
def temporary_table(cursor, temp_table, reference_table, columns):
    """Context manager for creating and dropping temp tables"""

    temp_table = Identifier(temp_table)
    reference_table = Identifier(reference_table)
    columns = SQL(",").join([Identifier(c) for c in columns])

    cursor.execute(
        CREATE_TEMP_TABLE_SQL.format(
            temp_table=temp_table,
            reference_table=reference_table,
            columns=columns,
        )
    )

    try:
        yield temp_table
    finally:
        cursor.execute(DROP_TEMPORARY_TABLE_SQL.format(temp_table=temp_table))


def grouper(it, n):
    it = iter(it)

    while True:
        try:
            first = next(it)
        except StopIteration:
            break
        slice = islice(it, n - 1)
        yield chain((first,), slice)


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("files", type=Path, nargs="+")

    def handle(self, files, **options):
        with tqdm(files) as file_bar, connection.cursor() as cursor:
            self.cursor = cursor
            for file in tqdm(files, postfix={"fichier": files[0].name}):
                file_bar.set_postfix(fichier=file.name)
                self.handle_file(file)

    def handle_file(self, file):
        with file.open("r", newline="") as fd:
            header_line = fd.readline()
            reader = csv.reader([header_line])
            columns = next(reader)
            del reader

            with temporary_table(
                self.cursor,
                "temp_table",
                "electeurs_electeur",
                columns,
            ) as temp_table:
                columns_list = SQL(",").join(Identifier(c) for c in columns)
                self.cursor.copy_expert(
                    COPY_SQL.format(
                        table=temp_table,
                        columns=columns_list,
                    ),
                    fd,
                )

                setters = [
                    Identifier(c) + SQL(" = ") + Identifier("excluded", c)
                    for c in columns
                    if c not in UNIQUE_FIELDS
                ]

                self.cursor.execute(
                    COPY_FROM_TEMP_TABLE.format(
                        table=Identifier("electeurs_electeur"),
                        temp_table=temp_table,
                        column_list=columns_list,
                        select_list=columns_list,
                        id_columns=SQL(",").join(
                            [Identifier(c) for c in UNIQUE_FIELDS]
                        ),
                        setters=SQL(",").join(setters),
                    ),
                )
