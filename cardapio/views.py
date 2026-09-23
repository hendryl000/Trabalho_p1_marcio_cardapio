from django.contrib import messages
from django.db import transaction
from django.db.models.deletion import ProtectedError
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST
from .forms import PratoForm, ComboForm, MesaForm, ItemForm
from .models import Prato, Combo, Mesa, Comanda, Item

def inicio(request):
    mesas = list(Mesa.objects.prefetch_related('comandas__itens'))
    for mesa in mesas:
        mesa.atual = next((c for c in mesa.comandas.all() if c.aberta), None)
    ocupadas = sum(mesa.atual is not None for mesa in mesas)
    return render(request, 'cardapio/inicio.html', {'mesas': mesas, 'ocupadas': ocupadas, 'livres': len(mesas) - ocupadas})

def filtrar_pratos(request, pratos):
    termo = request.GET.get('q', '').strip()
    categoria = request.GET.get('categoria', '')
    if termo:
        pratos = pratos.filter(nome__icontains=termo)
    if categoria:
        pratos = pratos.filter(categoria=categoria)
    return pratos


def menu(request):
    return render(request, 'cardapio/menu.html', {'pratos': filtrar_pratos(request, Prato.objects.filter(disponivel=True)), 'categorias': Prato.Categoria.choices, 'combos': Combo.objects.filter(disponivel=True).exclude(pratos__disponivel=False).prefetch_related('pratos').distinct()})

@require_POST
@transaction.atomic
def abrir(request, pk):
    mesa = get_object_or_404(Mesa.objects.select_for_update(), pk=pk)
    conta, _ = Comanda.objects.get_or_create(mesa=mesa, fechada_em=None)
    return redirect('comanda', pk=conta.pk)

@transaction.atomic
def comanda(request, pk):
    conta = get_object_or_404(Comanda.objects.select_for_update(), pk=pk)
    form = ItemForm(request.POST if request.method == 'POST' else None)
    if request.method == 'POST':
        if not conta.aberta:
            messages.error(request, 'Esta conta já está fechada e não pode ser alterada.')
            return redirect('comanda', pk=pk)
        if form.is_valid():
            item = form.save(commit=False)
            produto = item.prato or item.combo
            item.comanda = conta
            item.nome = produto.nome
            item.preco_unitario = produto.preco
            item.save()
            messages.success(request, 'Item adicionado à comanda.')
            return redirect('comanda', pk=pk)
    return render(request, 'cardapio/comanda.html', {'conta': conta, 'form': form})

@require_POST
@transaction.atomic
def remover_item(request, pk, item_pk):
    conta = get_object_or_404(Comanda.objects.select_for_update(), pk=pk)
    if conta.aberta:
        get_object_or_404(Item, pk=item_pk, comanda=conta).delete()
        messages.success(request, 'Item removido.')
    else:
        messages.error(request, 'Não é possível alterar uma conta fechada.')
    return redirect('comanda', pk=pk)

@transaction.atomic
def fechar(request, pk):
    conta = get_object_or_404(Comanda.objects.select_for_update(), pk=pk)
    if not conta.aberta:
        return redirect('comanda', pk=pk)
    if request.method == 'POST':
        conta.total_fechado = conta.total
        conta.fechada_em = timezone.now()
        conta.save(update_fields=['total_fechado', 'fechada_em'])
        messages.success(request, 'Conta fechada. A mesa está livre para outro atendimento.')
        return redirect('comanda', pk=pk)
    return render(request, 'cardapio/fechar.html', {'conta': conta})

def historico(request):
    return render(request, 'cardapio/historico.html', {'contas': Comanda.objects.filter(fechada_em__isnull=False).select_related('mesa')})

# Mesmo fluxo de ModelForm da Aula 5, reutilizado pelos três cadastros.
CADASTROS = {'pratos': (Prato, PratoForm, 'Pratos'), 'combos': (Combo, ComboForm, 'Combos'), 'mesas': (Mesa, MesaForm, 'Mesas')}

def cadastro(request, tipo, pk=None):
    if tipo not in CADASTROS:
        raise Http404
    model, form_class, titulo = CADASTROS[tipo]
    objeto = get_object_or_404(model, pk=pk) if pk else None
    form = form_class(request.POST if request.method == 'POST' else None, instance=objeto)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Cadastro salvo.')
        return redirect('cadastro', tipo=tipo)
    objetos = model.objects.all()
    if tipo == 'pratos':
        objetos = filtrar_pratos(request, objetos)
    return render(request, 'cardapio/cadastro.html', {'form': form, 'objetos': objetos, 'categorias': Prato.Categoria.choices, 'titulo': titulo, 'tipo': tipo, 'editando': objeto})

def excluir(request, tipo, pk):
    if tipo not in CADASTROS:
        raise Http404
    model, _, _ = CADASTROS[tipo]
    objeto = get_object_or_404(model, pk=pk)
    if request.method == 'POST':
        try:
            if tipo == 'pratos' and objeto.combos.exists():
                messages.error(request, 'Remova o prato dos combos antes de excluí-lo.')
            else:
                objeto.delete()
                messages.success(request, 'Cadastro excluído.')
        except ProtectedError:
            messages.error(request, 'Cadastro com histórico não pode ser excluído. Pratos e combos podem ser marcados como indisponíveis.')
        return redirect('cadastro', tipo=tipo)
    return render(request, 'cardapio/excluir.html', {'objeto': objeto, 'tipo': tipo})
