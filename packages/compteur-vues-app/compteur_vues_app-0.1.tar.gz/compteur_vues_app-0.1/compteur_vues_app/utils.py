from django.contrib.contenttypes.models import ContentType
from compteur_vues_app.models import Vue



def compter_vue(obj):
    """
    Incrémente et retourne le nombre de vues pour un objet Django donné.

    Paramètres :
    - obj : une instance de modèle Django (par exemple, un article, une page, etc.)

    Retourne :
    - Le nombre de vues actuel après incrémentation.
    """
    content_type = ContentType.objects.get_for_model(obj.__class__)
    vue, _ = Vue.objects.get_or_create(
        content_type=content_type,
        object_id=obj.pk
    )
    vue.increment_vues()
    return vue.vues
