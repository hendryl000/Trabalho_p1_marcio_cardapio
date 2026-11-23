from datetime import datetime
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone
from core.models import Organizacao
from cardapio.models import Prato, Combo, Mesa, Comanda, Item


class Command(BaseCommand):
    help = 'Cria vendas fictícias em uma organização exclusiva de demonstração, sem alterar vendas reais.'

    @transaction.atomic
    def handle(self, *args, **options):
        org, created = Organizacao.objects.get_or_create(nome='Restaurante demonstração · Dashboard')
        if not created and Comanda.objects.filter(organizacao=org).exists():
            self.stdout.write(f'Demonstração já existe na organização {org.pk}; nenhum registro alterado.')
            return
        mesa, _ = Mesa.objects.get_or_create(organizacao=org, numero=1)
        pratos = []
        for nome, preco, categoria in [('Filé da casa', '39.90', 'principal'), ('Risoto de cogumelos', '34.90', 'principal'),
                                        ('Suco de laranja', '8.00', 'bebida'), ('Pudim artesanal', '12.00', 'sobremesa')]:
            produto, _ = Prato.objects.get_or_create(organizacao=org, nome=nome,
                                                     defaults={'preco': preco, 'categoria': categoria})
            pratos.append(produto)
        combo, _ = Combo.objects.get_or_create(organizacao=org, nome='Almoço completo', defaults={'preco': '54.90'})
        combo.pratos.set([pratos[0], pratos[2], pratos[3]])
        hoje = timezone.localdate()
        for deslocamento in [2, 1, 0]:
            mes_absoluto = hoje.year * 12 + hoje.month - 1 - deslocamento
            ano, mes = divmod(mes_absoluto, 12)
            for indice, dia in enumerate([3, 7, 12, 18]):
                if deslocamento == 0 and dia > hoje.day:
                    continue
                fechado = timezone.make_aware(datetime(ano, mes + 1, dia, 20, 30))
                conta = Comanda.objects.create(organizacao=org, mesa=mesa, fechada_em=fechado, total_fechado=0)
                # Dados fictícios coerentes: a conta foi aberta antes do fechamento.
                Comanda.objects.filter(pk=conta.pk).update(aberta_em=fechado.replace(hour=19))
                produtos = [(pratos[indice % 2], indice + 1), (pratos[2], 2), (combo, 1)]
                for produto, quantidade in produtos:
                    Item.objects.create(organizacao=org, comanda=conta, nome=produto.nome,
                                        preco_unitario=produto.preco, quantidade=quantidade,
                                        **({'combo': produto} if isinstance(produto, Combo) else {'prato': produto}))
                conta.total_fechado = sum((produto.preco * quantidade for produto, quantidade in produtos), Decimal('0'))
                conta.save(update_fields=['total_fechado'])
        self.stdout.write(self.style.SUCCESS(f'Vendas fictícias criadas na organização {org.pk}: {org.nome}.'))
