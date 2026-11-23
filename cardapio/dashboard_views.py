import csv
from urllib.parse import urlencode
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseBadRequest, StreamingHttpResponse
from django.shortcuts import render
from django.utils import timezone
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_GET
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from core.tenancy import perfil_atual
from .dashboard import base_periodo, metricas, relatorio
from .forms import PeriodoForm


@login_required
@require_GET
@never_cache
def dashboard(request):
    perfil = perfil_atual(request)
    form = PeriodoForm(request.GET)
    contexto = {'form': form, 'mostra_series': perfil.eh_admin, 'org': perfil.organizacao}
    if not form.is_valid():
        return render(request, 'cardapio/dashboard.html', contexto, status=400)
    base = base_periodo(perfil.organizacao, form.cleaned_data)
    contexto.update(metricas(base, perfil.organizacao, incluir_serie=perfil.eh_admin))
    contexto['contas'] = list(relatorio(base)[:20])
    contexto['filtro_query'] = urlencode({key: value.isoformat() for key, value in form.cleaned_data.items() if value})
    return render(request, 'cardapio/dashboard.html', contexto)


class LinhaCSV:
    def write(self, value):
        return value


def celula_segura(value):
    value = str(value)
    if value.lstrip().startswith(('=', '+', '-', '@')) or value.startswith(('\t', '\r', '\n')):
        return "'" + value
    return value


@login_required
@require_GET
@never_cache
def exportar_csv(request):
    perfil = perfil_atual(request)
    if not perfil.eh_admin:
        raise PermissionDenied('Somente administradores podem exportar relatórios.')
    form = PeriodoForm(request.GET)
    if not form.is_valid():
        return HttpResponseBadRequest('Período inválido. Corrija as datas no dashboard antes de exportar.')
    base = base_periodo(perfil.organizacao, form.cleaned_data)
    writer = csv.writer(LinhaCSV(), delimiter=';')
    org_nome = celula_segura(perfil.organizacao.nome)

    def linhas():
        yield '\ufeff'  # UTF-8 com BOM para Excel.
        yield writer.writerow(['Organização', 'Comanda', 'Mesa', 'Abertura', 'Fechamento', 'Total (R$)'])
        for conta in relatorio(base).iterator(chunk_size=1000):
            yield writer.writerow([org_nome, conta.pk, conta.mesa.numero,
                                   timezone.localtime(conta.aberta_em).strftime('%d/%m/%Y %H:%M:%S'),
                                   timezone.localtime(conta.fechada_em).strftime('%d/%m/%Y %H:%M:%S'),
                                   format(conta.total_fechado or 0, '.2f').replace('.', ',')])

    response = StreamingHttpResponse(linhas(), content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = 'attachment; filename="comandas.csv"'
    return response


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@never_cache
def dashboard_api(request):
    perfil = perfil_atual(request)
    form = PeriodoForm(request.query_params)
    if not form.is_valid():
        return Response({'erros': form.errors.get_json_data()}, status=400)
    base = base_periodo(perfil.organizacao, form.cleaned_data)
    dados = metricas(base, perfil.organizacao, incluir_serie=perfil.eh_admin)
    dados['periodo'] = form.cleaned_data
    return Response(dados)
