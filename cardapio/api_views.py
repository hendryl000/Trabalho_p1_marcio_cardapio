from core.tenancy import org_atual
from django.db.models.deletion import ProtectedError
from rest_framework import generics
from rest_framework.exceptions import ValidationError

from .models import Prato
from .serializers import PratoSerializer


class PratoDaOrganizacao:
    serializer_class = PratoSerializer

    def get_queryset(self):
        return Prato.objects.filter(organizacao=org_atual(self.request))

    def perform_create(self, serializer):
        serializer.save(organizacao=org_atual(self.request))


class PratoListCreate(PratoDaOrganizacao, generics.ListCreateAPIView):
    pass


class PratoDetail(PratoDaOrganizacao, generics.RetrieveUpdateDestroyAPIView):

    def perform_destroy(self, instance):
        if instance.combos.exists():
            raise ValidationError({
                'detail': 'Remova o prato dos combos antes de excluí-lo.'
            })
        try:
            instance.delete()
        except ProtectedError:
            raise ValidationError({
                'detail': 'Prato com histórico não pode ser excluído. '
                          'Marque-o como indisponível.'
            })
