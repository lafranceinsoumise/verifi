import argparse
import csv
from itertools import chain, islice

from django.core.management import BaseCommand

DEFAULT_BULK_SIZE = 10000

REQUIRED_COLUMNS = {
    "type_liste",
    "nom",
    "nom_usage",
    "prénoms",
    "sexe",
    "date_naissance",
    "bureau",
    "num_électeur",
    "date_export",
}


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
        parser.add_argument(
            "files",
            type=argparse.FileType(mode="r"),
        )
        parser.add_argument("--bulk-size", type=int, default=DEFAULT_BULK_SIZE)

    def handle(self, files, bulk_size, **options):
        for file in files:
            self.handle_file(file, bulk_size)

    def handle_file(self, file, bulk_size):
        reader = csv.reader(file)
