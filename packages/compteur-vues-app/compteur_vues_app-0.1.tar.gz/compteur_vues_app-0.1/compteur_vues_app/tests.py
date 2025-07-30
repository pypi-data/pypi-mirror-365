from django.test import TestCase
from django.urls import reverse
from ..models.models import Vue  # Correction de l'importation


class CompteurVuesTests(TestCase):
    def setUp(self):
        """Création d'un objet pour tester l'incrémentation des vues"""
        self.object_type = 'article'
        self.object_id = 1
        self.url = reverse('afficher_vue', kwargs={'object_type': self.object_type, 'object_id': self.object_id})

    def test_initial_vue(self):
        """Vérifier qu'un objet n'a pas de vues initiales"""
        response = self.client.get(self.url)
        vue = Vue.objects.get(object_type=self.object_type, object_id=self.object_id)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(vue.compteur, 1)  # Première vue après la création

    def test_increment_vue(self):
        """Vérifier que le compteur de vues s'incrémente à chaque requête"""
        self.client.get(self.url)  # Première vue
        self.client.get(self.url)  # Deuxième vue
        vue = Vue.objects.get(object_type=self.object_type, object_id=self.object_id)
        self.assertEqual(vue.compteur, 2)  # Le compteur doit être incrémenté

    def test_template_usage(self):
        """Vérifier que le bon template est utilisé"""
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, 'compteur_vues_app/my_template.html')  # Correction du chemin