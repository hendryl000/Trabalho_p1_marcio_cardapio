import csv
import io
from datetime import date, datetime
from decimal import Decimal
from zoneinfo import ZoneInfo
from django.contrib.auth import get_user_model
from django.db import connection
from django.test import TestCase
from django.test.utils import CaptureQueriesContext
from django.utils import timezone
from rest_framework.test import APIClient
from core.models import Organizacao, Perfil
from .dashboard import base_periodo, metricas, relatorio
from .dashboard_views import celula_segura
from .forms import PeriodoForm
from .models import Comanda, Combo, Item, Mesa, Prato


TZ = ZoneInfo('America/Sao_Paulo')


class DashboardTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.org = Organizacao.objects.create(nome='Restaurante A')
        cls.outra = Organizacao.objects.create(nome='Restaurante B')
        cls.admin = get_user_model().objects.create_user('gestor')
        cls.operador = get_user_model().objects.create_user('operador')
        cls.admin_b = get_user_model().objects.create_user('gestor_b')
        Perfil.objects.create(usuario=cls.admin, organizacao=cls.org, papel='admin')
        Perfil.objects.create(usuario=cls.operador, organizacao=cls.org)
        Perfil.objects.create(usuario=cls.admin_b, organizacao=cls.outra, papel='admin')
        cls.mesa = Mesa.objects.create(organizacao=cls.org, numero=1)
        cls.prato = Prato.objects.create(organizacao=cls.org, nome='Prato A', preco='10')
        cls.combo = Combo.objects.create(organizacao=cls.org, nome='Combo A', preco='30')
        cls.combo.pratos.add(cls.prato)
        cls.contas = []
        for data, produto, quantidade in [
            (datetime(2026, 10, 31, 23, 59, 59, 999999, tzinfo=TZ), cls.prato, 2),
            (datetime(2026, 11, 1, tzinfo=TZ), cls.combo, 1),
            (datetime(2026, 11, 23, 23, 59, 59, 999999, tzinfo=TZ), cls.prato, 4),
        ]:
            conta = Comanda.objects.create(organizacao=cls.org, mesa=cls.mesa,
                                          fechada_em=data, total_fechado=produto.preco * quantidade)
            Item.objects.create(organizacao=cls.org, comanda=conta, nome=produto.nome,
                                preco_unitario=produto.preco, quantidade=quantidade,
                                **({'prato': produto} if isinstance(produto, Prato) else {'combo': produto}))
            cls.contas.append(conta)
        cls.aberta = Comanda.objects.create(organizacao=cls.org, mesa=cls.mesa)
        Item.objects.create(organizacao=cls.org, comanda=cls.aberta, prato=cls.prato,
                            nome='Não faturado', preco_unitario='100', quantidade=99)
        mesa_b = Mesa.objects.create(organizacao=cls.outra, numero=1)
        prato_b = Prato.objects.create(organizacao=cls.outra, nome='Segredo B', preco='9000')
        cls.conta_b = Comanda.objects.create(organizacao=cls.outra, mesa=mesa_b,
                                            fechada_em=datetime(2026, 11, 10, tzinfo=TZ), total_fechado='9000')
        Item.objects.create(organizacao=cls.outra, comanda=cls.conta_b, prato=prato_b,
                            nome=prato_b.nome, preco_unitario=prato_b.preco)

    def setUp(self):
        self.client.force_login(self.admin)
        self.api = APIClient()
        self.api.force_login(self.admin)

    def test_quatro_metricas_conferidas_a_mao(self):
        r = self.client.get('/dashboard/')
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.context['kpis'], {'faturamento': Decimal('90'), 'comandas': 3,
                                           'ticket_medio': Decimal('30'), 'itens': 7})
        self.assertEqual([(x['nome'], x['unidades']) for x in r.context['ranking']], [('Prato A', 6), ('Combo A', 1)])
        self.assertEqual(r.context['distribuicao'], [{'tipo': 'Pratos', 'quantidade': 6}, {'tipo': 'Combos', 'quantidade': 1}])
        self.assertEqual([(s['mes'], s['faturamento']) for s in r.context['serie']], [('10/2026', Decimal('20')), ('11/2026', Decimal('70'))])
        self.assertEqual(sum(x['faturamento'] for x in r.context['serie']), r.context['kpis']['faturamento'])
        self.assertNotContains(r, 'Segredo B')
        self.assertNotContains(r, 'Não faturado')

    def test_periodo_inclusivo_fuso_local_e_todos_componentes(self):
        periodo = {'inicio': '2026-11-01', 'fim': '2026-11-23'}
        r = self.client.get('/dashboard/', periodo)
        self.assertEqual(r.context['kpis']['faturamento'], Decimal('70'))
        self.assertEqual(r.context['kpis']['ticket_medio'], Decimal('35'))
        self.assertEqual(r.context['kpis']['itens'], 5)
        self.assertEqual(len(r.context['serie']), 1)
        self.assertEqual(r.context['distribuicao'][0]['quantidade'], 4)
        self.assertCountEqual([c.pk for c in r.context['contas']], [c.pk for c in self.contas[1:]])
        self.assertContains(r, 'inicio=2026-11-01&amp;fim=2026-11-23')
        self.assertEqual(self.client.get('/dashboard/', {'fim': '2026-10-31'}).context['kpis']['faturamento'], Decimal('20'))
        self.assertEqual(self.client.get('/dashboard/', {'inicio': '2026-11-23', 'fim': '2026-11-23'}).context['kpis']['faturamento'], Decimal('40'))

    def test_periodos_invalidos_nao_retornam_dados_sem_filtro(self):
        for periodo in [{'inicio': 'abc'}, {'fim': '2026-02-30'}, {'inicio': '2026-12-01', 'fim': '2026-11-01'}, {'fim': '9999-12-31'}]:
            with self.subTest(periodo=periodo):
                response = self.client.get('/dashboard/', periodo)
                self.assertEqual(response.status_code, 400)
                self.assertNotIn('kpis', response.context)
                self.assertEqual(self.client.get('/dashboard/exportar.csv', periodo).status_code, 400)
                self.assertEqual(self.api.get('/api/dashboard/', periodo).status_code, 400)

    def test_vazio_sem_erro(self):
        r = self.client.get('/dashboard/', {'inicio': '2030-01-01'})
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.context['kpis']['faturamento'], 0)
        self.assertEqual(r.context['kpis']['ticket_medio'], 0)
        self.assertEqual(r.context['ranking'], [])
        self.assertEqual(r.context['serie'], [])
        self.assertContains(r, 'Sem comandas fechadas')

    def test_papel_operador_sem_serie_e_sem_csv_mesmo_por_url(self):
        self.client.force_login(self.operador)
        self.api.force_login(self.operador)
        r = self.client.get('/dashboard/')
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.context['kpis']['comandas'], 3)
        self.assertNotContains(r, 'dados-vendas')
        self.assertNotContains(r, 'Exportar CSV')
        self.assertNotIn('serie', self.api.get('/api/dashboard/').data)
        self.assertEqual(self.client.get('/dashboard/exportar.csv').status_code, 403)

    def test_anonimo_e_sem_perfil(self):
        self.client.logout()
        self.api.logout()
        self.assertEqual(self.client.get('/dashboard/').status_code, 302)
        self.assertEqual(self.client.get('/dashboard/exportar.csv').status_code, 302)
        self.assertEqual(self.api.get('/api/dashboard/').status_code, 403)
        sem_perfil = get_user_model().objects.create_user('sem_perfil')
        self.client.force_login(sem_perfil)
        self.api.force_login(sem_perfil)
        self.assertEqual(self.client.get('/dashboard/').status_code, 403)
        self.assertEqual(self.client.get('/dashboard/exportar.csv').status_code, 403)
        self.assertEqual(self.api.get('/api/dashboard/').status_code, 403)

    def test_api_reutiliza_metricas_e_ignora_org_da_url(self):
        periodo = {'inicio': '2026-11-01', 'organizacao': self.outra.pk}
        r = self.api.get('/api/dashboard/', periodo)
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.data['kpis']['faturamento'], Decimal('70'))
        self.assertEqual(r.data['kpis'], self.client.get('/dashboard/', periodo).context['kpis'])
        self.assertIn('no-store', r['Cache-Control'])
        self.api.force_login(self.admin_b)
        self.assertEqual(self.api.get('/api/dashboard/').data['kpis']['faturamento'], Decimal('9000'))

    def test_csv_mesma_base_com_filtro_e_acentos(self):
        response = self.client.get('/dashboard/exportar.csv', {'inicio': '2026-11-01', 'fim': '2026-11-23'})
        self.assertEqual(response.status_code, 200)
        body = b''.join(response.streaming_content).decode('utf-8-sig')
        rows = list(csv.reader(io.StringIO(body), delimiter=';'))
        self.assertEqual(len(rows), 3)
        self.assertEqual(rows[0][0], 'Organização')
        self.assertEqual(sum(Decimal(row[-1].replace(',', '.')) for row in rows[1:]), Decimal('70'))
        self.assertTrue(all(row[0] == self.org.nome for row in rows[1:]))
        self.assertNotIn('9000', body)
        self.assertIn('attachment;', response['Content-Disposition'])
        self.assertIn('no-store', response['Cache-Control'])

    def test_csv_neutraliza_formulas(self):
        for value in ['=1+1', '+1+1', '-1+1', '@SUM(A1)', '  =2+2', '\t=1+1']:
            self.assertTrue(celula_segura(value).startswith("'"))
        self.assertEqual(celula_segura('À Mesa'), 'À Mesa')
        self.org.nome = '=HYPERLINK("https://exemplo.invalid")'
        self.org.save()
        r = self.client.get('/dashboard/exportar.csv')
        rows = list(csv.reader(io.StringIO(b''.join(r.streaming_content).decode('utf-8-sig')), delimiter=';'))
        self.assertTrue(rows[1][0].startswith("'="))

    def test_precos_historicos_e_top_cinco(self):
        self.prato.preco = Decimal('999')
        self.prato.nome = 'Nome atual'
        self.prato.save()
        dados = metricas(base_periodo(self.org, {}), self.org, True)
        self.assertEqual(dados['kpis']['faturamento'], Decimal('90'))
        self.assertEqual(dados['ranking'][0]['nome'], 'Prato A')
        self.assertEqual(dados['ranking'][0]['valor'], Decimal('60'))
        for index in range(7):
            produto = Prato.objects.create(organizacao=self.org, nome=f'Produto {index}', preco='1')
            Item.objects.create(organizacao=self.org, comanda=self.contas[0], prato=produto,
                                nome=produto.nome, preco_unitario=produto.preco)
        self.assertEqual(len(metricas(base_periodo(self.org, {}), self.org)['ranking']), 5)

    def test_consultas_metricas_e_relatorio_constantes(self):
        base = base_periodo(self.org, {})
        with self.assertNumQueries(5):
            metricas(base, self.org, incluir_serie=True)
            for conta in relatorio(base):
                str(conta.mesa)
        for i in range(50):
            Comanda.objects.create(organizacao=self.org, mesa=self.mesa,
                                   fechada_em=datetime(2026, 11, 20, tzinfo=TZ), total_fechado='10')
        with self.assertNumQueries(5):
            metricas(base, self.org, incluir_serie=True)
            for conta in relatorio(base):
                str(conta.mesa)
        with self.assertNumQueries(1):
            for conta in relatorio(base):
                str(conta.mesa)

    def test_sem_n_mais_um_no_salao_e_dashboard_renderizados(self):
        with CaptureQueriesContext(connection) as pequeno:
            self.client.get('/')
        with CaptureQueriesContext(connection) as dash_pequeno:
            self.client.get('/dashboard/')
        for i in range(2, 12):
            mesa = Mesa.objects.create(organizacao=self.org, numero=i)
            conta = Comanda.objects.create(organizacao=self.org, mesa=mesa)
            Item.objects.create(organizacao=self.org, comanda=conta, prato=self.prato,
                                nome=self.prato.nome, preco_unitario=self.prato.preco)
        with CaptureQueriesContext(connection) as grande:
            self.client.get('/')
        with CaptureQueriesContext(connection) as dash_grande:
            self.client.get('/dashboard/')
        self.assertEqual(len(pequeno), len(grande))
        self.assertEqual(len(dash_pequeno), len(dash_grande))
        self.assertLessEqual(len(grande), 10)
        self.assertLessEqual(len(dash_grande), 10)
        print(f'Consultas: salão {len(pequeno)} -> {len(grande)}; dashboard {len(dash_pequeno)} -> {len(dash_grande)}')
