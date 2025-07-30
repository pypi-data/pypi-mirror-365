## Application compteur de vues

Un package Django simple et efficace pour compter automatiquement le nombre de fois qu'un article a été vu.


## 1- Installation

 --Installez le package via pip :
```bash
pip install compteur_vues_app

```

## 2- Guide d'installation étape par étape

-- Ajoutez le package à vos INSTALLED_APPS dans votre fichier settings.py :


## 3- Configuration des URLs

--Ajoutez les URLs du package dans votre urls.py principal


  ## Migrations 

```bash
python manage.py makemigrations
python manage.py migrate
```


  ## Créer un superutilisateur

-- python manage.py createsuperuser


  ##  Création d'articles via l'interface d'administration
-- Accédez à l'interface d'administration : http://127.0.0.1:8000/admin/
-- Connectez-vous avec vos identifiants de superutilisateur
-- Créez vos articles dans la section correspondante


  ## 4- Visualisation et comptage des vues

Pour voir un article et incrémenter automatiquement son compteur de vues :

http://127.0.0.1:8000/article/{id}/
Remplacez {id} par l'ID réel de votre article (ex: http://127.0.0.1:8000/article/1/).

##  5- Fonctionnalités
-- Comptage automatique des vues d'articles
-- Interface d'administration Django intégrée
-- Incrémentation automatique lors de l'accès à article/{id}/
-- Simple à installer et configurer
-- Compatible avec les projets Django existants


















`compteur_vues_app` est une application Django réutilisable qui permet de comptabiliser et d’afficher le nombre de vues pour n’importe quel objet (ex : article, page, etc.). L'application propose une interface simple, stylisée, prête à l'emploi.

---

## 🚀 Installation

1. Clonez ou installez le package localement :

```bash
pip install -e ./compteur_vues_app