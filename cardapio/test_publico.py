from django.test import TestCase
from django.urls import reverse
from core.models import Organizacao
from .models import Prato, Combo


class CardapioPublicoTests(TestCase):
    def setUp(self):
        self.org = Organizacao.objects.create(nome='Restaurante A')
        self.outra = Organizacao.objects.create(nome='Restaurante B')
        self.prato = Prato.objects.create(organizacao=self.org, nome='Risoto A', preco='20', categoria='principal')
        self.oculto = Prato.objects.create(organizacao=self.org, nome='Prato oculto', preco='10', disponivel=False)
        self.alheio = Prato.objects.create(organizacao=self.outra, nome='Segredo B', preco='30')
        self.combo = Combo.objects.create(organizacao=self.org, nome='Combo disponível', preco='25')
        self.combo.pratos.add(self.prato)
        self.indisponivel = Combo.objects.create(organizacao=self.org, nome='Combo indisponível', preco='25')
        self.indisponivel.pratos.add(self.oculto)
        self.url = reverse('cardapio_publico', args=[self.org.pk])

    def test_publico_isolado_sem_login_e_sem_dados_internos(self):
        response = self.client.get(self.url)
        self.assertContains(response, 'Risoto A')
        self.assertContains(response, 'Combo disponível')
        for texto in ['Segredo B', 'Prato oculto', 'Combo indisponível', '/cadastros/', '/historico/']:
            self.assertNotContains(response, texto)
        self.assertEqual(len(response.context['catalogo']), 2)
        self.assertEqual(self.client.post(self.url, {'nome': 'Injetado'}).status_code, 405)
        self.assertEqual(self.client.get(reverse('cardapio_publico', args=[999999])).status_code, 404)
        self.assertEqual(self.client.get('/api/pratos/').status_code, 403)
        self.assertEqual(self.client.get('/cadastros/pratos/').status_code, 302)

    def test_filtros_sem_javascript_e_estado_vazio(self):
        response = self.client.get(self.url, {'q': 'RISOTO', 'categoria': 'principal'})
        self.assertEqual([p['nome'] for p in response.context['visiveis']], ['Risoto A'])
        response = self.client.get(self.url, {'q': 'inexistente'})
        self.assertEqual(response.context['visiveis'], [])
        vazia = Organizacao.objects.create(nome='Novo restaurante')
        self.assertContains(self.client.get(reverse('cardapio_publico', args=[vazia.pk])), 'O cardápio está sendo preparado.')

    def test_combo_vazio_ou_corrompido_nao_e_publicado(self):
        Combo.objects.create(organizacao=self.org, nome='Combo vazio', preco='20')
        # Simula dados inseridos fora do fluxo validado (SQL/importação antiga).
        Combo.pratos.through.objects.create(combo=self.combo, prato=self.alheio)
        response = self.client.get(self.url)
        self.assertNotContains(response, 'Combo vazio')
        self.assertNotContains(response, 'Combo disponível')
        self.assertNotContains(response, 'Segredo B')

    def test_conteudo_do_catalogo_escapado(self):
        self.prato.nome = '<script>alert(1)</script>'
        self.prato.save()
        response = self.client.get(self.url)
        self.assertNotContains(response, '<script>alert(1)</script>')
        self.assertContains(response, '&lt;script&gt;')
