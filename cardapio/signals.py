from django.core.exceptions import ValidationError
from django.db.models.signals import m2m_changed
from django.dispatch import receiver
from .models import Combo, Prato


@receiver(m2m_changed, sender=Combo.pratos.through)
def validar_organizacao_dos_pratos(sender, instance, action, reverse, pk_set, **kwargs):
    if action != 'pre_add' or not pk_set:
        return
    model = Combo if reverse else Prato
    if model.objects.filter(pk__in=pk_set).exclude(organizacao_id=instance.organizacao_id).exists():
        raise ValidationError('Combo e pratos devem pertencer à mesma organização.')
