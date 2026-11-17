from rest_framework import serializers

from .models import Prato


class PratoSerializer(serializers.ModelSerializer):
    # ModelSerializer reaproveita o MinValueValidator do campo preco do model.
    class Meta:
        model = Prato
        fields = ['id', 'nome', 'descricao', 'categoria', 'preco', 'disponivel']
        read_only_fields = ['id']
