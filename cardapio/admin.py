from django.contrib import admin
from django import forms
from core.admin import SomenteSuperusuario
from .models import Prato, Combo, Mesa, Comanda, Item


class ComboAdminForm(forms.ModelForm):
    class Meta:
        model = Combo
        fields = ['organizacao', 'nome', 'descricao', 'pratos', 'preco', 'disponivel']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        org_id = self.instance.organizacao_id if self.instance.pk else self.data.get('organizacao')
        try:
            org_id = int(org_id)
        except (ValueError, TypeError):
            org_id = None
        self.fields['pratos'].queryset = Prato.objects.filter(organizacao_id=org_id)
        self.fields['pratos'].help_text = 'Salve a organização antes de selecionar os pratos ao criar um combo.'
        self.fields['pratos'].required = False


@admin.register(Prato)
class PratoAdmin(SomenteSuperusuario):
    list_display = ['nome', 'organizacao', 'preco', 'disponivel']
    list_filter = ['organizacao']
    def get_readonly_fields(self, request, obj=None):
        return ['organizacao'] if obj else []


@admin.register(Combo)
class ComboAdmin(PratoAdmin):
    form = ComboAdminForm


@admin.register(Mesa)
class MesaAdmin(PratoAdmin):
    list_display = ['numero', 'organizacao', 'capacidade']


class ConsultaAdmin(SomenteSuperusuario):
    list_display = ['__str__', 'organizacao']
    list_filter = ['organizacao']
    def has_add_permission(self, request):
        return False
    def has_change_permission(self, request, obj=None):
        return False
    def has_delete_permission(self, request, obj=None):
        return False


admin.site.register(Comanda, ConsultaAdmin)
admin.site.register(Item, ConsultaAdmin)
