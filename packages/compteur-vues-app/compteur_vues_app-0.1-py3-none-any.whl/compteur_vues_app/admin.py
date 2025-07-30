from django.contrib import admin
from .models import Vue, Article

@admin.register(Vue)
class VueAdmin(admin.ModelAdmin):
    list_display = ('object_type', 'object_id', 'vues')

    def object_type(self, obj):
        return obj.content_type.model.capitalize()
    object_type.short_description = 'Type d’objet'

@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ('id', 'titre', 'contenu')