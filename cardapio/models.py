from decimal import Decimal
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import Q

class Prato(models.Model):
    class Categoria(models.TextChoices):
        ENTRADA = 'entrada', 'Entradas'
        PRINCIPAL = 'principal', 'Pratos principais'
        ACOMPANHAMENTO = 'acompanhamento', 'Acompanhamentos'
        SOBREMESA = 'sobremesa', 'Sobremesas'
        BEBIDA = 'bebida', 'Bebidas'
        OUTROS = 'outros', 'Outros'

    categoria = models.CharField(max_length=20, choices=Categoria.choices, default=Categoria.OUTROS)
    nome = models.CharField(max_length=100)
    descricao = models.TextField('descrição', blank=True)
    preco = models.DecimalField('preço', max_digits=8, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    disponivel = models.BooleanField('disponível', default=True)
    class Meta:
        ordering = ['nome']
    def __str__(self):
        return self.nome

class Combo(models.Model):
    nome = models.CharField(max_length=100)
    descricao = models.TextField('descrição', blank=True)
    pratos = models.ManyToManyField(Prato, related_name='combos')
    preco = models.DecimalField('preço', max_digits=8, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    disponivel = models.BooleanField('disponível', default=True)
    class Meta:
        ordering = ['nome']
    def __str__(self):
        return self.nome

class Mesa(models.Model):
    numero = models.PositiveIntegerField('número', unique=True, validators=[MinValueValidator(1)])
    capacidade = models.PositiveIntegerField(default=4, validators=[MinValueValidator(1)])
    class Meta:
        ordering = ['numero']
    def __str__(self):
        return f'Mesa {self.numero:02d}'

class Comanda(models.Model):
    mesa = models.ForeignKey(Mesa, on_delete=models.PROTECT, related_name='comandas')
    aberta_em = models.DateTimeField(auto_now_add=True)
    fechada_em = models.DateTimeField(null=True, blank=True)
    total_fechado = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    class Meta:
        ordering = ['-aberta_em']
        constraints = [models.UniqueConstraint(fields=['mesa'], condition=Q(fechada_em__isnull=True), name='uma_comanda_aberta_por_mesa')]
    @property
    def aberta(self):
        return self.fechada_em is None
    @property
    def total(self):
        if not self.aberta:
            return self.total_fechado
        return sum((item.subtotal for item in self.itens.all()), Decimal('0.00'))
    def __str__(self):
        return f'Comanda #{self.pk} - {self.mesa}'

class Item(models.Model):
    comanda = models.ForeignKey(Comanda, on_delete=models.PROTECT, related_name='itens')
    prato = models.ForeignKey(Prato, on_delete=models.PROTECT, null=True, blank=True)
    combo = models.ForeignKey(Combo, on_delete=models.PROTECT, null=True, blank=True)
    # Cópias preservam o pedido mesmo quando o cardápio muda.
    nome = models.CharField(max_length=100)
    preco_unitario = models.DecimalField(max_digits=8, decimal_places=2)
    quantidade = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])
    observacao = models.CharField('observação', max_length=200, blank=True)
    class Meta:
        ordering = ['id']
        constraints = [
            models.CheckConstraint(condition=(Q(prato__isnull=False, combo__isnull=True) | Q(prato__isnull=True, combo__isnull=False)), name='item_prato_ou_combo'),
            models.CheckConstraint(condition=Q(quantidade__gte=1), name='quantidade_positiva'),
        ]
    @property
    def subtotal(self):
        return self.preco_unitario * self.quantidade
    def __str__(self):
        return f'{self.quantidade}x {self.nome}'
