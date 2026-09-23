from django.core.management.base import BaseCommand
from cardapio.models import Prato, Combo, Mesa

class Command(BaseCommand):
    help = 'Cria um cardápio de exemplo e seis mesas, sem apagar registros.'
    def handle(self, *args, **options):
        dados = [
            ('Filé da casa', 'Filé grelhado com arroz, feijão e batatas douradas.', '39.90'),
            ('Frango grelhado', 'Peito de frango com arroz e legumes frescos.', '28.90'),
            ('Risoto de cogumelos', 'Arroz cremoso com cogumelos e parmesão.', '34.90'),
            ('Batata rústica', 'Batatas douradas com ervas e molho da casa.', '16.00'),
            ('Suco de laranja', 'Suco natural de laranja, copo de 300 ml.', '8.00'),
            ('Pudim artesanal', 'Pudim de leite com calda de caramelo.', '12.00'),
        ]
        pratos = {}
        for nome, descricao, preco in dados:
            pratos[nome], _ = Prato.objects.get_or_create(nome=nome, defaults={'descricao': descricao, 'preco': preco})
        for nome, descricao, preco, componentes in [
            ('Almoço completo', 'O clássico da casa com bebida e sobremesa.', '54.90', ['Filé da casa', 'Suco de laranja', 'Pudim artesanal']),
            ('Combo leve', 'Uma pausa saborosa com frango e suco natural.', '32.90', ['Frango grelhado', 'Suco de laranja']),
        ]:
            combo, criado = Combo.objects.get_or_create(nome=nome, defaults={'descricao': descricao, 'preco': preco})
            if criado:
                combo.pratos.set([pratos[n] for n in componentes])
        for numero in range(1, 7):
            Mesa.objects.get_or_create(numero=numero, defaults={'capacidade': 4 if numero < 5 else 6})
        self.stdout.write(self.style.SUCCESS('Cardápio de exemplo e mesas prontos.'))
