from decimal import Decimal
from django.test import TestCase, Client
from django.urls import reverse
from .models import Prato, Combo, Mesa, Comanda, Item

class AtendimentoTests(TestCase):
    def setUp(self):
        self.mesa = Mesa.objects.create(numero=1)
        self.prato = Prato.objects.create(nome='Prato teste', preco='19.90')
        self.combo = Combo.objects.create(nome='Combo teste', preco='25.00')
        self.combo.pratos.add(self.prato)
        self.client.post(reverse('abrir', args=[self.mesa.pk]))
        self.conta = Comanda.objects.get()
        self.url = reverse('comanda', args=[self.conta.pk])

    def adicionar(self, **kwargs):
        dados = {'prato': self.prato.pk, 'quantidade': 2}
        dados.update(kwargs)
        return self.client.post(self.url, dados)

    def test_ciclo_completo_e_preco_preservado(self):
        self.adicionar()
        self.adicionar(prato='', combo=self.combo.pk, quantidade=1)
        self.assertEqual(self.conta.total, Decimal('64.80'))
        self.prato.preco = Decimal('99.00')
        self.prato.save()
        self.assertEqual(self.conta.total, Decimal('64.80'))
        self.client.post(reverse('fechar', args=[self.conta.pk]))
        self.conta.refresh_from_db()
        self.assertFalse(self.conta.aberta)
        self.assertEqual(self.conta.total_fechado, Decimal('64.80'))
        self.adicionar()
        self.assertEqual(self.conta.itens.count(), 2)
        self.client.post(reverse('remover_item', args=[self.conta.pk, self.conta.itens.first().pk]))
        self.assertEqual(self.conta.itens.count(), 2)
        self.client.post(reverse('abrir', args=[self.mesa.pk]))
        self.assertEqual(Comanda.objects.count(), 2)
        self.assertContains(self.client.get(reverse('historico')), '64,80')

    def test_abertura_repetida_reutiliza_comanda(self):
        self.client.post(reverse('abrir', args=[self.mesa.pk]))
        self.assertEqual(Comanda.objects.count(), 1)

    def test_valida_quantidade_e_produto(self):
        for dados in [{'quantidade': 0}, {'quantidade': -1}, {'prato': '', 'combo': ''}, {'combo': self.combo.pk}]:
            self.assertEqual(self.adicionar(**dados).status_code, 200)
        self.assertEqual(Item.objects.count(), 0)
        self.prato.disponivel = False
        self.prato.save()
        self.adicionar()
        self.adicionar(prato='', combo=self.combo.pk)
        self.assertEqual(Item.objects.count(), 0)

    def test_remocao_recalcula_e_nao_acessa_outra_comanda(self):
        self.adicionar()
        item = Item.objects.get()
        outra = Comanda.objects.create(mesa=Mesa.objects.create(numero=2))
        self.assertEqual(self.client.post(reverse('remover_item', args=[outra.pk, item.pk])).status_code, 404)
        self.client.post(reverse('remover_item', args=[self.conta.pk, item.pk]))
        self.assertEqual(self.conta.total, Decimal('0.00'))

    def test_get_nao_muda_estado_e_csrf(self):
        self.assertEqual(self.client.get(reverse('abrir', args=[self.mesa.pk])).status_code, 405)
        self.client.get(reverse('fechar', args=[self.conta.pk]))
        self.conta.refresh_from_db()
        self.assertTrue(self.conta.aberta)
        client = Client(enforce_csrf_checks=True)
        self.assertEqual(client.post(reverse('abrir', args=[self.mesa.pk])).status_code, 403)

    def test_telas_e_cadastros(self):
        for url in ['/', '/cardapio/', '/historico/', '/cadastros/pratos/', '/cadastros/combos/', '/cadastros/mesas/', self.url]:
            self.assertEqual(self.client.get(url).status_code, 200, url)
        self.client.post('/cadastros/pratos/', {'nome': 'Sobremesa', 'categoria': 'sobremesa', 'preco': '12.50', 'disponivel': 'on'})
        prato = Prato.objects.get(nome='Sobremesa')
        self.client.post(f'/cadastros/pratos/{prato.pk}/', {'nome': 'Doce', 'categoria': 'sobremesa', 'preco': '13.50', 'disponivel': 'on'})
        prato.refresh_from_db()
        self.assertEqual(prato.nome, 'Doce')
        self.client.post(f'/cadastros/pratos/{prato.pk}/excluir/')
        self.assertFalse(Prato.objects.filter(pk=prato.pk).exists())

    def test_preserva_cadastros_com_historico(self):
        self.adicionar()
        self.client.post(f'/cadastros/mesas/{self.mesa.pk}/excluir/')
        self.client.post(f'/cadastros/pratos/{self.prato.pk}/excluir/')
        self.assertTrue(Mesa.objects.filter(pk=self.mesa.pk).exists())
        self.assertTrue(Prato.objects.filter(pk=self.prato.pk).exists())
