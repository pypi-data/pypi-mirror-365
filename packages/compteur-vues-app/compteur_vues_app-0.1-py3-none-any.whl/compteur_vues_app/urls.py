from django.urls import path
from compteur_vues_app.views.views import afficher_vue
from django.http import HttpResponse


urlpatterns = [
    path('', lambda request: HttpResponse("Bienvenue sur la page d'accueil du compteur")),
    path('<str:object_type>/<int:object_id>/', afficher_vue, name='afficher_vue'),
]
