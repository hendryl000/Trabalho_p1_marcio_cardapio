from decimal import Decimal
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import transaction
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient
from core.models import Organizacao, Perfil
from .forms import ComboForm, ItemForm, MesaForm
from .models import Prato, Combo, Mesa, Comanda, Item


class IsolamentoTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.a = Organizacao.objects.create(nome='Restaurante A')
        cls.b = Organizacao.objects.create(nome='Restaurante B')
        cls.ua = get_user_model().objects.create_user('usuario_a', password='teste-a-123')
        cls.ub = get_user_model().objects.create_user('usuario_b', password='teste-b-123')
        Perfil.objects.create(usuario=cls.ua, organizacao=cls.a)
        Perfil.objects.create(usuario=cls.ub, organizacao=cls.b)
        for suffix, org in [('a', cls.a), ('b', cls.b)]:
            prato = Prato.objects.create(organizacao=org, nome=f'Prato exclusivo {suffix}', preco='10.00')
            combo = Combo.objects.create(organizacao=org, nome=f'Combo exclusivo {suffix}', preco='15.00')
            combo.pratos.add(prato)
            mesa = Mesa.objects.create(organizacao=org, numero=1)
            conta = Comanda.objects.create(organizacao=org, mesa=mesa)
            item = Item.objects.create(organizacao=org, comanda=conta, prato=prato,
                                       nome=prato.nome, preco_unitario=prato.preco)
            for name, value in [('prato', prato), ('combo', combo), ('mesa', mesa), ('conta', conta), ('item', item)]:
                setattr(cls, name+'_'+suffix, value)

    def setUp(self):
        self.client.force_login(self.ua)
        self.api = APIClient()
        self.api.force_login(self.ua)

    def test_listas_e_busca_nos_dois_sentidos(self):
        for user, org, prato, combo, mesa in [
            (self.ua, self.a, self.prato_a, self.combo_a, self.mesa_a),
            (self.ub, self.b, self.prato_b, self.combo_b, self.mesa_b),
        ]:
            self.client.force_login(user)
            self.api.force_login(user)
            self.assertEqual(list(self.client.get('/').context['mesas']), [mesa])
            menu = self.client.get('/cardapio/')
            self.assertEqual(list(menu.context['pratos']), [prato])
            self.assertEqual(list(menu.context['combos']), [combo])
            for tipo, registro in [('pratos', prato), ('combos', combo), ('mesas', mesa)]:
                self.assertEqual(list(self.client.get(reverse('cadastro', args=[tipo])).context['objetos']), [registro])
            self.assertEqual([p['id'] for p in self.api.get('/api/pratos/').data], [prato.pk])
            self.assertEqual(list(self.client.get('/cardapio/', {'q': 'exclusivo'}).context['pratos']), [prato])

    def test_ids_alheios_html_retornam_404_sem_alterar(self):
        for tipo, objeto in [('pratos', self.prato_b), ('combos', self.combo_b), ('mesas', self.mesa_b)]:
            for rota in ['editar', 'excluir']:
                url = reverse(rota, args=[tipo, objeto.pk])
                self.assertEqual(self.client.get(url).status_code, 404)
                self.assertEqual(self.client.post(url, {}).status_code, 404)
        self.assertEqual(self.client.post(reverse('abrir', args=[self.mesa_b.pk])).status_code, 404)
        for rota in ['comanda', 'fechar']:
            url = reverse(rota, args=[self.conta_b.pk])
            self.assertEqual(self.client.get(url).status_code, 404)
            self.assertEqual(self.client.post(url, {}).status_code, 404)
        for conta in [self.conta_a, self.conta_b]:
            self.assertEqual(self.client.post(reverse('remover_item', args=[conta.pk, self.item_b.pk])).status_code, 404)
        self.conta_b.refresh_from_db()
        self.assertTrue(self.conta_b.aberta)
        self.assertTrue(Item.objects.filter(pk=self.item_b.pk).exists())

    def test_ids_alheios_api_retornam_404(self):
        url = reverse('api:prato-detail', args=[self.prato_b.pk])
        for method in ['get', 'put', 'patch', 'delete']:
            self.assertEqual(getattr(self.api, method)(url, {}, format='json').status_code, 404)
        self.prato_b.refresh_from_db()
        self.assertEqual(self.prato_b.preco, Decimal('10.00'))

    def test_criacao_e_patch_nao_aceitam_organizacao_do_cliente(self):
        dados = {'nome': 'Criado via HTML', 'preco': '9.50', 'categoria': 'outros', 'organizacao': self.b.pk}
        self.assertEqual(self.client.post('/cadastros/pratos/', dados).status_code, 302)
        self.assertEqual(Prato.objects.get(nome=dados['nome']).organizacao, self.a)
        dados['nome'] = 'Criado via API'
        resposta = self.api.post('/api/pratos/', dados, format='json')
        self.assertEqual(resposta.status_code, 201)
        criado = Prato.objects.get(pk=resposta.data['id'])
        self.assertEqual(criado.organizacao, self.a)
        self.assertEqual(self.api.patch(reverse('api:prato-detail', args=[criado.pk]), {'organizacao': self.b.pk, 'nome': 'Atualizado'}, format='json').status_code, 200)
        criado.refresh_from_db()
        self.assertEqual(criado.organizacao, self.a)

    def test_selects_e_post_de_relacionamentos_alheios(self):
        form = self.client.get('/cadastros/combos/').context['form']
        self.assertEqual(list(form.fields['pratos'].queryset), [self.prato_a])
        form = self.client.get(reverse('comanda', args=[self.conta_a.pk])).context['form']
        self.assertEqual(list(form.fields['prato'].queryset), [self.prato_a])
        self.assertEqual(list(form.fields['combo'].queryset), [self.combo_a])
        for produto in [{'prato': self.prato_b.pk}, {'combo': self.combo_b.pk}]:
            resposta = self.client.post(reverse('comanda', args=[self.conta_a.pk]), {**produto, 'quantidade': 1})
            self.assertEqual(resposta.status_code, 200)
            self.assertTrue(resposta.context['form'].errors)
        resposta = self.client.post('/cadastros/combos/', {'nome': 'Ataque', 'preco': '10', 'pratos': [self.prato_b.pk]})
        self.assertTrue(resposta.context['form'].errors)
        self.assertFalse(Combo.objects.filter(nome='Ataque').exists())
        self.assertEqual(self.conta_a.itens.count(), 1)

    def test_mesa_igual_em_org_distinta_e_duplicado_amigavel(self):
        self.assertEqual(self.mesa_a.numero, self.mesa_b.numero)
        resposta = self.client.post('/cadastros/mesas/', {'numero': 1, 'capacidade': 4})
        self.assertContains(resposta, 'Já existe uma mesa')
        self.assertEqual(Mesa.objects.filter(organizacao=self.a).count(), 1)
        form = MesaForm({'numero': 1, 'capacidade': 6}, instance=self.mesa_a, org=self.a)
        self.assertTrue(form.is_valid(), form.errors)

    def test_atendimento_grava_org_e_historico_isolado(self):
        self.client.post(reverse('comanda', args=[self.conta_a.pk]), {'prato': self.prato_a.pk, 'quantidade': 2, 'organizacao': self.b.pk})
        self.assertEqual(self.conta_a.itens.order_by('-id').first().organizacao, self.a)
        self.client.post(reverse('fechar', args=[self.conta_a.pk]))
        self.conta_b.fechada_em = timezone.now()
        self.conta_b.total_fechado = Decimal('10')
        self.conta_b.save()
        self.assertEqual(list(self.client.get('/historico/').context['contas']), [self.conta_a])
        self.client.post(reverse('abrir', args=[self.mesa_a.pk]))
        self.assertEqual(Comanda.objects.get(mesa=self.mesa_a, fechada_em=None).organizacao, self.a)

    def test_anonimo_e_usuario_sem_perfil(self):
        self.client.logout()
        for url in ['/', '/cardapio/', '/historico/', '/cadastros/pratos/', reverse('comanda', args=[self.conta_a.pk])]:
            self.assertEqual(self.client.get(url).status_code, 302)
        sem_perfil = get_user_model().objects.create_superuser('sem_perfil', password='teste-123')
        self.client.force_login(sem_perfil)
        self.api.force_login(sem_perfil)
        for url in ['/', '/cardapio/', '/historico/', '/cadastros/pratos/']:
            self.assertEqual(self.client.get(url).status_code, 403)
        self.assertEqual(self.api.get('/api/pratos/').status_code, 403)
        self.assertEqual(self.api.post('/api/pratos/', {'nome': 'Sem org', 'preco': '10'}, format='json').status_code, 403)
        self.assertEqual(self.client.get('/admin/core/organizacao/').status_code, 200)

    def test_models_impedem_relacionamentos_cruzados(self):
        with self.assertRaises(ValidationError), transaction.atomic():
            Comanda.objects.create(organizacao=self.a, mesa=self.mesa_b)
        with self.assertRaises(ValidationError), transaction.atomic():
            Item.objects.create(organizacao=self.a, comanda=self.conta_a, prato=self.prato_b, nome='Inválido', preco_unitario='10')
        with self.assertRaises(ValidationError), transaction.atomic():
            self.combo_a.pratos.add(self.prato_b)
        with self.assertRaises(ValidationError), transaction.atomic():
            self.prato_a.combos.add(self.combo_b)

    def test_admin_de_negocio_reservado_ao_dono_do_sistema(self):
        from django.contrib.auth.models import Permission
        self.ua.is_staff = True
        self.ua.save()
        self.ua.user_permissions.add(*Permission.objects.filter(content_type__app_label__in=['core', 'cardapio']))
        self.assertEqual(self.client.get('/admin/cardapio/prato/').status_code, 403)
        self.assertEqual(self.client.get('/admin/core/perfil/').status_code, 403)
