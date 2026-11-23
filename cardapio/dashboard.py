"""Perguntas semanais: quanto vendemos, o que mais sai, como evolui e qual o mix?

Uma base de comandas fechadas sustenta todas as métricas, o relatório e o CSV.
Período = data de fechamento no fuso do restaurante (America/Sao_Paulo).
"""
from datetime import datetime, time, timedelta
from decimal import Decimal
from django.db.models import Avg, Count, DecimalField, ExpressionWrapper, F, Q, Sum
from django.db.models.functions import TruncMonth
from django.utils import timezone
from .models import Comanda, Item


def base_periodo(org, periodo):
    base = Comanda.objects.filter(organizacao=org, fechada_em__isnull=False)
    inicio, fim = periodo.get('inicio'), periodo.get('fim')
    if inicio:
        base = base.filter(fechada_em__gte=timezone.make_aware(datetime.combine(inicio, time.min)))
    if fim:
        # Limite exclusivo no dia seguinte: inclui todo o último dia, inclusive microssegundos.
        base = base.filter(fechada_em__lt=timezone.make_aware(datetime.combine(fim + timedelta(days=1), time.min)))
    return base


def relatorio(base):
    return base.select_related('mesa').order_by('-fechada_em', '-pk')


def metricas(base, org, incluir_serie=False):
    kpis = base.aggregate(
        faturamento=Sum('total_fechado', default=Decimal('0.00')),
        comandas=Count('pk'),
        ticket_medio=Avg('total_fechado', default=Decimal('0.00')),
    )
    itens = Item.objects.filter(organizacao=org, comanda__in=base.order_by().values('pk'))
    mix = itens.aggregate(
        pratos=Sum('quantidade', filter=Q(prato__isnull=False), default=0),
        combos=Sum('quantidade', filter=Q(combo__isnull=False), default=0),
    )
    kpis['itens'] = mix['pratos'] + mix['combos']
    total_item = ExpressionWrapper(F('quantidade') * F('preco_unitario'),
                                   output_field=DecimalField(max_digits=18, decimal_places=2))
    ranking = list(itens.values('prato_id', 'combo_id', 'nome').annotate(
        unidades=Sum('quantidade'), valor=Sum(total_item)
    ).order_by('-unidades', 'nome', 'prato_id', 'combo_id')[:5])
    dados = {'kpis': kpis, 'ranking': ranking, 'distribuicao': [
        {'tipo': 'Pratos', 'quantidade': mix['pratos']},
        {'tipo': 'Combos', 'quantidade': mix['combos']},
    ]}
    if incluir_serie:
        serie = base.annotate(mes=TruncMonth('fechada_em', tzinfo=timezone.get_current_timezone())).values('mes').annotate(
            faturamento=Sum('total_fechado', default=Decimal('0.00')), comandas=Count('pk')
        ).order_by('mes')
        dados['serie'] = [{'mes': row['mes'].strftime('%m/%Y'),
                          'faturamento': row['faturamento'], 'comandas': row['comandas']} for row in serie]
    return dados
