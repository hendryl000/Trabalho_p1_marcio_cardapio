from django.contrib import admin
from .models import Prato, Combo, Mesa, Comanda, Item
admin.site.register(Prato)
admin.site.register(Combo)
admin.site.register(Mesa)

class ConsultaAdmin(admin.ModelAdmin):
    # Atendimento passa pelas views para preservar as regras da conta.
    def has_add_permission(self, request):
        return False
    def has_change_permission(self, request, obj=None):
        return False
    def has_delete_permission(self, request, obj=None):
        return False
admin.site.register(Comanda, ConsultaAdmin)
admin.site.register(Item, ConsultaAdmin)
