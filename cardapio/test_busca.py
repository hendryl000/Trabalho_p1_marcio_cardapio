from core.models import Organizacao, Perfil
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from .models import Prato


class BuscaPratosTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.org = Organizacao.objects.create(nome='Restaurante testes')
        cls.user = get_user_model().objects.create_user('teste_busca')
        Perfil.objects.create(usuario=cls.user, organizacao=cls.org)
        cls.bolo = Prato.objects.create(organizacao=cls.org, nome='Bolo de chocolate', preco='12.00', categoria='sobremesa')
        cls.bebida = Prato.objects.create(organizacao=cls.org, nome='Chocolate quente', preco='8.00', categoria='bebida')
        cls.oculto = Prato.objects.create(organizacao=cls.org, nome='Bolo indisponível', preco='10.00', categoria='sobremesa', disponivel=False)

    def setUp(self):
        self.client.force_login(self.user)

    def test_busca_categoria_e_combinacao(self):
        for url, chave in [(reverse('menu'), 'pratos'), (reverse('cadastro', args=['pratos']), 'objetos')]:
            for filtros, esperados in [
                ({}, [self.bolo, self.bebida]),
                ({'q': '  CHOCOLATE  '}, [self.bolo, self.bebida]),
                ({'categoria': 'bebida'}, [self.bebida]),
                ({'q': 'chocolate', 'categoria': 'sobremesa'}, [self.bolo]),
                ({'q': 'inexistente'}, []),
                ({'categoria': 'invalida'}, []),
            ]:
                with self.subTest(url=url, filtros=filtros):
                    resposta = self.client.get(url, filtros)
                    previstos = list(esperados)
                    if chave == 'objetos' and not filtros:
                        previstos.append(self.oculto)
                    self.assertCountEqual(resposta.context[chave], previstos)

    def test_filtros_preservados_e_mensagem_vazia(self):
        for url in [reverse('menu'), reverse('cadastro', args=['pratos'])]:
            resposta = self.client.get(url, {'q': 'Sem resultado', 'categoria': 'bebida'})
            self.assertContains(resposta, 'value="Sem resultado"')
            self.assertContains(resposta, 'value="bebida" selected')
            self.assertContains(resposta, 'Nenhum prato encontrado com os filtros informados.')

    def test_categoria_no_cadastro_e_edicao(self):
        url = reverse('cadastro', args=['pratos'])
        dados = {'nome': 'Suco', 'categoria': 'bebida', 'preco': '9.50', 'disponivel': 'on'}
        self.assertRedirects(self.client.post(url, dados), url)
        prato = Prato.objects.get(nome='Suco')
        self.assertEqual(prato.categoria, 'bebida')
        dados['categoria'] = 'outros'
        self.client.post(reverse('editar', args=['pratos', prato.pk]), dados)
        prato.refresh_from_db()
        self.assertEqual(prato.categoria, 'outros')
