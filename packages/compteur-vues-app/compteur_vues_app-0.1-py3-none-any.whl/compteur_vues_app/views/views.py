from django.shortcuts import render
from django.contrib.contenttypes.models import ContentType
from django.http import Http404
from ..models import Vue

def afficher_vue(request, object_type, object_id):
    """Affiche et incrémente le compteur de vues pour un objet donné."""

    # 1. Vérifier que le ContentType existe
    try:
        content_type = ContentType.objects.get(model=object_type)
    except ContentType.DoesNotExist:
        raise Http404(f"Le modèle '{object_type}' n'existe pas dans ContentType.")

    # 2. Vérifier que l'objet de ce type avec cet ID existe
    model_class = content_type.model_class()
    try:
        instance = model_class.objects.get(pk=object_id)
    except model_class.DoesNotExist:
        raise Http404(f"L'objet de type '{object_type}' avec l'ID {object_id} n'existe pas.")

    # 3. Récupérer ou créer une instance Vue
    vue, _ = Vue.objects.get_or_create(object_id=object_id, content_type=content_type)

    # 4. Incrémenter les vues
    vue.increment_vues()

    # 5. Contexte pour le template
    context = {
        'object_type': object_type,
        'object_id': object_id,
        'compteur': vue.vues,
        'objet': instance  # tu peux l'afficher dans le template si tu veux
    }

    return render(request, 'compteur_vues_app/my_template.html', context)
