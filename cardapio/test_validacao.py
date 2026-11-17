from core.models import Organizacao, Perfil
from django.contrib.auth import get_user_model
from decimal import Decimal
from django.test import TestCase
from django.urls import reverse
from .forms import PratoForm
from .models import Prato


class ValidacaoPrecoTests(TestCase):
    def setUp(self):
        self.org = Organizacao.objects.create(nome='Restaurante testes')
        self.user = get_user_model().objects.create_user('teste_local')
        Perfil.objects.create(usuario=self.user, organizacao=self.org)
        self.client.force_login(self.user)

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
            form = PratoForm(org=self.org, data={'nome': 'Teste', 'categoria': 'outros', 'preco': preco})
            self.assertTrue(form.is_valid(), form.errors)
            self.assertEqual(form.cleaned_data['preco'], Decimal(preco))
        for preco in ['', 'abc']:
            form = PratoForm(org=self.org, data={'nome': 'Teste', 'categoria': 'outros', 'preco': preco})
            self.assertFalse(form.is_valid())
            self.assertIn('preco', form.errors)
