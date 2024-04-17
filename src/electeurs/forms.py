from django import forms
from django.core import validators

from electeurs.actions import TypeElection


class RechercheElecteurForm(forms.Form):
    code_com = forms.CharField(label="Code commune", max_length=5, required=True)
    date_naissance = forms.CharField(
        label="Date de naissance",
        validators=[validators.RegexValidator(r"^\d{2}/\d{2}/\d{4}$")],
        required=True,
    )
    nom = forms.CharField(label="Nom de famille (ou d'usage", required=True)
    prenoms = forms.CharField(label="Prénoms (tous)", required=True)
    election = forms.ChoiceField(
        label="Scrutin",
        choices=[(e, e) for e in TypeElection],
        initial=TypeElection.autre,
    )
