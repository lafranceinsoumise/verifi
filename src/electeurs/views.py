from django.http import JsonResponse
from django.shortcuts import render

from electeurs.actions import verifier_electeur
from electeurs.forms import RechercheElecteurForm

PARAMS = ["code_com", "date_naissance", "nom", "prenoms", "election"]


def verifier_electeur_view(request):
    if request.method == "GET":
        f = RechercheElecteurForm(request.GET)

        if not f.is_valid():
            return JsonResponse(
                {"status": "error", "type": "wrong inputs", "errors": f.errors},
                status=400,
            )

        electeur = verifier_electeur(**f.cleaned_data)

        if not electeur:
            return JsonResponse({"status": "not found"})

        return JsonResponse({"status": "found", **electeur.to_json()})

    return JsonResponse({"status": "error", "type": "wrong method"})
