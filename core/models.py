from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models


class Organizacao(models.Model):
    nome = models.CharField(max_length=120)
    criada_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nome


class Perfil(models.Model):
    usuario = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='perfil')
    organizacao = models.ForeignKey(Organizacao, on_delete=models.PROTECT)

    def __str__(self):
        return f'{self.usuario} — {self.organizacao}'


class DaOrganizacao(models.Model):
    organizacao = models.ForeignKey(Organizacao, on_delete=models.PROTECT)

    class Meta:
        abstract = True

    def clean(self):
        super().clean()
        # Impede vínculos FK cruzados também fora dos formulários.
        if not self.organizacao_id:
            return
        errors = {}
        for field in self._meta.fields:
            if isinstance(field, models.ForeignKey) and issubclass(field.related_model, DaOrganizacao):
                related_id = getattr(self, field.attname)
                if related_id and not field.related_model.objects.filter(
                    pk=related_id, organizacao_id=self.organizacao_id
                ).exists():
                    errors[field.name] = 'Selecione um registro da mesma organização.'
        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)
