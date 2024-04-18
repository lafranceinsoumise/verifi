from django.http import JsonResponse

from electeurs.actions import verifier_electeur, verifier_commune
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

        if not verifier_commune(f.cleaned_data["code_com"]):
            return JsonResponse({"status": "commune manquante"})

        electeur = verifier_electeur(**f.cleaned_data)

        if not electeur:
            return JsonResponse({"status": "pas inscrit"})

        return JsonResponse({"status": "inscrit", "electeur": electeur.to_json()})

    return JsonResponse({"status": "error", "type": "wrong method"})
