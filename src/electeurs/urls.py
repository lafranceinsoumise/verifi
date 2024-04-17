from django.urls import path

from electeurs.views import verifier_electeur_view

app_name = "electeurs"

urlpatterns = [
    path("verifier", verifier_electeur_view, name="verifier"),
]
