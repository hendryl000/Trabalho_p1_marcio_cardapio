from decimal import Decimal
from django.test import TestCase
from django.urls import reverse
from .forms import PratoForm
from .models import Prato


class ValidacaoPrecoTests(TestCase):
    def test_preco_invalido_exibe_erro_e_nao_salva(self):
        for preco in ['0', '-1.00']:
            with self.subTest(preco=preco):
                resposta = self.client.post(reverse('cadastro', args=['pratos']), {
                    'nome': 'Teste', 'categoria': 'outros', 'preco': preco,
                })
                self.assertContains(resposta, 'O preço do prato deve ser maior que zero.')
                self.assertFalse(Prato.objects.exists())

    def test_preco_positivo_e_campos_invalidos(self):
        for preco in ['0.01', '12.50']:
            form = PratoForm(data={'nome': 'Teste', 'categoria': 'outros', 'preco': preco})
            self.assertTrue(form.is_valid(), form.errors)
            self.assertEqual(form.cleaned_data['preco'], Decimal(preco))
        for preco in ['', 'abc']:
            form = PratoForm(data={'nome': 'Teste', 'categoria': 'outros', 'preco': preco})
            self.assertFalse(form.is_valid())
            self.assertIn('preco', form.errors)
