from django.db.models.deletion import ProtectedError
from rest_framework import generics
from rest_framework.exceptions import ValidationError

from .models import Prato
from .serializers import PratoSerializer


class PratoListCreate(generics.ListCreateAPIView):
    queryset = Prato.objects.all()
    serializer_class = PratoSerializer


class PratoDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Prato.objects.all()
    serializer_class = PratoSerializer

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
