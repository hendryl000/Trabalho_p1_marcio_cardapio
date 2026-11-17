from core.models import Organizacao, Perfil
from django.contrib.auth import get_user_model
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient, APITestCase

from .models import Combo, Comanda, Item, Mesa, Prato


class PratoAPITests(APITestCase):
    def setUp(self):
        self.org = Organizacao.objects.create(nome='Restaurante testes')
        self.user = get_user_model().objects.create_user('teste', password='senha-teste-123')
        Perfil.objects.create(usuario=self.user, organizacao=self.org)
        self.client.login(username='teste', password='senha-teste-123')
        self.url = reverse('api:prato-list')
        self.dados = {'nome': 'Arroz', 'descricao': 'Porção', 'categoria': 'acompanhamento',
                      'preco': '12.50', 'disponivel': True}
        self.prato = Prato.objects.create(organizacao=self.org, **self.dados)
        self.detail = reverse('api:prato-detail', args=[self.prato.pk])

    def test_crud_com_sessao(self):
        resposta = self.client.get(self.url)
        self.assertEqual(resposta.status_code, 200)
        self.assertEqual(set(resposta.data[0]), {'id', 'nome', 'descricao', 'categoria', 'preco', 'disponivel'})
        resposta = self.client.post(self.url, self.dados, format='json')
        self.assertEqual(resposta.status_code, 201)
        url = reverse('api:prato-detail', args=[resposta.data['id']])
        self.assertEqual(self.client.get(url).status_code, 200)
        self.assertEqual(self.client.put(url, {**self.dados, 'nome': 'Feijão'}, format='json').status_code, 200)
        self.assertEqual(self.client.patch(url, {'disponivel': False}, format='json').status_code, 200)
        self.assertFalse(Prato.objects.get(pk=resposta.data['id']).disponivel)
        self.assertEqual(self.client.delete(url).status_code, 204)
        self.assertEqual(self.client.get(url).status_code, 404)

    def test_anonimo_nao_acessa_crud(self):
        self.client.logout()
        for method, url in [('get', self.url), ('post', self.url), ('get', self.detail),
                            ('put', self.detail), ('patch', self.detail), ('delete', self.detail)]:
            with self.subTest(method=method, url=url):
                self.assertEqual(getattr(self.client, method)(url).status_code, 403)
        self.assertEqual(Prato.objects.count(), 1)

    def test_validacoes_na_criacao_e_atualizacao(self):
        for campo, valor in [('preco', '0'), ('preco', '-1'), ('preco', 'abc'),
                             ('preco', '1.001'), ('categoria', 'invalida'), ('nome', '')]:
            with self.subTest(campo=campo, valor=valor):
                resposta = self.client.post(self.url, {**self.dados, campo: valor}, format='json')
                self.assertEqual(resposta.status_code, 400)
                self.assertIn(campo, resposta.data)
                self.assertEqual(self.client.patch(self.detail, {campo: valor}, format='json').status_code, 400)
        self.assertEqual(Prato.objects.count(), 1)
        self.assertEqual(self.client.post(self.url, {}, format='json').status_code, 400)
        self.assertEqual(self.client.post(self.url, {**self.dados, 'preco': '0.01'}, format='json').status_code, 201)

    def test_exclusao_preserva_combo(self):
        combo = Combo.objects.create(organizacao=self.org, nome='Almoço', preco='20.00')
        combo.pratos.add(self.prato)
        self.assertEqual(self.client.delete(self.detail).status_code, 400)
        self.assertTrue(combo.pratos.filter(pk=self.prato.pk).exists())

    def test_exclusao_preserva_historico(self):
        mesa = Mesa.objects.create(organizacao=self.org, numero=1)
        comanda = Comanda.objects.create(organizacao=self.org, mesa=mesa)
        Item.objects.create(organizacao=self.org, comanda=comanda, prato=self.prato, nome=self.prato.nome,
                            preco_unitario=self.prato.preco)
        self.assertEqual(self.client.delete(self.detail).status_code, 400)
        self.assertTrue(Prato.objects.filter(pk=self.prato.pk).exists())

    def test_sessao_exige_csrf_para_escrita(self):
        cliente = APIClient(enforce_csrf_checks=True)
        cliente.login(username='teste', password='senha-teste-123')
        self.assertEqual(cliente.post(self.url, self.dados, format='json').status_code, 403)
        pagina = cliente.get(self.url, HTTP_ACCEPT='text/html')
        self.assertEqual(pagina.status_code, 200)
        token = cliente.cookies['csrftoken'].value
        self.assertEqual(cliente.post(self.url, self.dados, format='json', HTTP_X_CSRFTOKEN=token).status_code, 201)

    def test_login_navegavel(self):
        self.assertEqual(self.client.get(reverse('rest_framework:login')).status_code, 200)
