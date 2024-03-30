import csv
import logging
import re
import sys
from pathlib import Path

import pandas as pd
from django.core.management import BaseCommand, CommandError
from pandas._typing import ReadCsvBuffer
from tqdm import tqdm

logger = logging.getLogger(__name__)


def lower_than_warning(record: logging.LogRecord):
    return record.levelno < logging.WARNING


# Normaliser les noms de colonnes
FIELDNAMES_SUBS = {
    "code de l'ugle": "code_com",
    "code du l'ugle": "code_com",
    "libellé du type de liste": "type_liste",
    "nom de naissance": "nom",
    "nom d'usage": "nom_usage",
    "prénoms": "prenoms",
    "date de naissance": "date_naissance",
    "pays de naissance": "pays_naissance",
    "code de la commune de naissance": "commune_naissance",
    "numéro de voie": "num_voie",
    "libellé de voie": "voie",
    "complément 1": "comp1",
    "complément 2": "comp2",
    "lieu-dit": "lieu_dit",
    "code postal": "code_postal",
    "code du bureau de vote": "bureau",
    "numéro d'ordre dans le bureau de vote": "num_electeur",
    "nationalité": "nationalite",
}

TYPE_LIST_SUBS = {
    "lp": "LP",
    "lcm": "LCM",
    "lce": "LCE",
    "liste principale": "LP",
    "liste complémentaire municipale": "LCM",
    "liste complémentaire européenne": "LCE",
}

REQUIRED_FIELDS = [
    "code_com",
    "type_liste",
    "nom",
    "nom_usage",
    "prenoms",
    "sexe",
    "date_naissance",
    "bureau",
    "num_electeur",
    "date_export",
]

ADDITIONAL_INFORMATION_FIELDS = [
    "commune_naissance",
    "pays_naissance",
    "nationalite",
]

ADDRESS_FIELDS = [
    "num_voie",
    "voie",
    "comp1",
    "comp2",
    "lieu_dit",
    "code_postal",
    "commune",
    "pays",
]

DEST_HEADER = [*REQUIRED_FIELDS, *ADDITIONAL_INFORMATION_FIELDS, *ADDRESS_FIELDS]

COM_RE = re.compile(r"com(\d[\dAB]\d{3})")
TYPE_LISTE_RE = re.compile(r"LP|LCE|LCM")
DATE_EXPORT_RE = re.compile(r"(\d{2})-(\d{2})-(\d{4})")


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("source_dir", type=Path)
        parser.add_argument("target_dir", type=Path)

    def handle(self, source_dir, target_dir, verbosity, **options):
        self.errors = []
        self.verbosity = verbosity
        self.source_dir = source_dir

        error_handler = logging.StreamHandler(sys.stderr)
        error_handler.setLevel(logging.WARNING)
        debug_handler = logging.StreamHandler(sys.stdout)
        debug_handler.addFilter(lower_than_warning)
        logger.addHandler(error_handler)
        logger.addHandler(debug_handler)
        logger.setLevel(
            {0: logging.ERROR, 1: logging.WARNING, 2: logging.INFO, 3: logging.DEBUG}[
                verbosity
            ]
        )

        if not source_dir.is_dir():
            raise CommandError("SOURCE_DIR doit être un répertoire existant")

        if not target_dir.is_dir():
            try:
                target_dir.mkdir(parents=True)
            except OSError:
                raise CommandError(
                    "TARGET_DIR n'est pas un répertoire ou ne peut pas être créé"
                )

        rep_deps = sorted(d for d in source_dir.iterdir() if d.is_dir())

        with tqdm(rep_deps, postfix={"dep": rep_deps[0].name}) as bar:
            for dep in bar:
                bar.set_postfix(dep=dep.name)
                numero_dep = dep.name.split()[0]
                logger.info(f"Traitement département N°{numero_dep}")
                target_file = target_dir / f"{numero_dep}.csv"
                with target_file.open("w") as fdout:
                    self.handle_dep(dep, fdout)

    def trouver_separateur(self, fh):
        pos = fh.tell()
        header_line = fh.readline()
        fh.seek(pos)

        if "," in header_line:
            return ","
        elif ";" in header_line:
            return ";"
        else:
            raise ValueError("N'est pas un fichier CSV")

    def handle_dep(self, dep, dest):
        files = dep.glob("*.csv")

        writer = csv.DictWriter(
            dest,
            fieldnames=DEST_HEADER,
            extrasaction="ignore",
        )
        writer.writeheader()
        del writer

        for f in files:
            self.message(f, "Début du traitement", logging.DEBUG)

            defaults = {}

            if match := COM_RE.search(f.name):
                defaults["code_com"] = match.group(1)
            if match := TYPE_LISTE_RE.search(f.name):
                defaults["type_liste"] = match.group(0)
            if match := DATE_EXPORT_RE.search(f.name):
                defaults["date_export"] = (
                    f"{match.group(3)}-{match.group(2)}-{match.group(1)}"
                )

            fd: ReadCsvBuffer[str]
            with f.open("r") as fd:
                try:
                    sep = self.trouver_separateur(fd)
                except ValueError:
                    self.message(
                        f, "Impossible de détecter le séparateur", logging.ERROR
                    )
                    continue

                reader = csv.reader(fd, delimiter=sep)

                headers = next(reader)
                del reader
                fd.seek(0)

                names = [FIELDNAMES_SUBS.get(h, h) for h in headers]

                all_fields = set(names).union(defaults)

                missing_required_fields = set(REQUIRED_FIELDS).difference(all_fields)
                if missing_required_fields:
                    self.message(
                        f,
                        f"Champs obligatoires manquants : {','.join(missing_required_fields)}",
                        logging.ERROR,
                    )
                    continue

                missing_additional_information_fields = set(
                    ADDITIONAL_INFORMATION_FIELDS
                ).difference(all_fields)
                if missing_additional_information_fields:
                    self.message(
                        f,
                        f"Champs d'état civil manquants : {','.join(missing_additional_information_fields)}",
                        logging.INFO,
                    )

                missing_address_fields = set(ADDRESS_FIELDS).difference(all_fields)
                if missing_address_fields:
                    self.message(
                        f,
                        f"Champs d'adresse manquants : {','.join(missing_address_fields)}",
                        logging.WARNING,
                    )

                for chunk in pd.read_csv(
                    fd,
                    delimiter=sep,
                    header=None,
                    skiprows=1,
                    names=names,
                    usecols=[n for n in names if n in DEST_HEADER],
                    dtype={n: str for n in names},
                    chunksize=int(2e5),
                ):

                    for k, v in defaults.items():
                        if k in chunk.columns:
                            chunk[k] = chunk[k].fillna(v)
                        else:
                            chunk[k] = v

                    # élimine le préfixe 'com' si présent
                    chunk["code_com"] = chunk["code_com"].str.slice(-5)

                    chunk["type_liste"] = (
                        chunk["type_liste"].str.lower().map(TYPE_LIST_SUBS)
                    )

                    chunk[
                        chunk.bureau.notnull() & chunk.num_electeur.notnull()
                    ].reindex(columns=DEST_HEADER).to_csv(
                        dest, index=False, header=False
                    )

    def message(self, file, message, level):
        rel_path = file.relative_to(self.source_dir)
        logger.log(level, f"{rel_path}: {message}")
