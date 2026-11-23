from django.contrib import admin
from .models import Organizacao, Perfil


class SomenteSuperusuario(admin.ModelAdmin):
    def has_module_permission(self, request):
        return request.user.is_superuser

    def has_view_permission(self, request, obj=None):
        return request.user.is_superuser

    has_add_permission = has_view_permission
    has_change_permission = has_view_permission
    has_delete_permission = has_view_permission


@admin.register(Organizacao)
class OrganizacaoAdmin(SomenteSuperusuario):
    list_display = ['nome', 'criada_em']


@admin.register(Perfil)
class PerfilAdmin(SomenteSuperusuario):
    list_display = ['usuario', 'organizacao', 'papel']
    list_filter = ['organizacao', 'papel']
