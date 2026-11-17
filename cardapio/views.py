from django.contrib.auth.decorators import login_required
from django.db.models import Prefetch
from core.tenancy import org_atual
from django.contrib import messages
from django.db import transaction
from django.db.models.deletion import ProtectedError
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST, require_GET
from .forms import PratoForm, ComboForm, MesaForm, ItemForm
from .models import Prato, Combo, Mesa, Comanda, Item

@login_required
def inicio(request):
    mesas = list(Mesa.objects.filter(organizacao=org_atual(request)).prefetch_related(Prefetch('comandas', queryset=Comanda.objects.filter(organizacao=org_atual(request), fechada_em__isnull=True))))
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


@login_required
def menu(request):
    return render(request, 'cardapio/menu.html', {'pratos': filtrar_pratos(request, Prato.objects.filter(organizacao=org_atual(request), disponivel=True)), 'categorias': Prato.Categoria.choices, 'combos': Combo.objects.filter(organizacao=org_atual(request), disponivel=True).exclude(pratos__disponivel=False).prefetch_related(Prefetch('pratos', queryset=Prato.objects.filter(organizacao=org_atual(request)))).distinct()})

@require_POST
@transaction.atomic
@login_required
def abrir(request, pk):
    mesa = get_object_or_404(Mesa.objects.select_for_update(), pk=pk, organizacao=org_atual(request))
    conta, _ = Comanda.objects.get_or_create(mesa=mesa, fechada_em=None, organizacao=org_atual(request))
    return redirect('comanda', pk=conta.pk)

@transaction.atomic
@login_required
def comanda(request, pk):
    conta = get_object_or_404(Comanda.objects.select_for_update().prefetch_related(Prefetch('itens', queryset=Item.objects.filter(organizacao=org_atual(request)))), pk=pk, organizacao=org_atual(request))
    form = ItemForm(request.POST if request.method == 'POST' else None, org=org_atual(request))
    if request.method == 'POST':
        if not conta.aberta:
            messages.error(request, 'Esta conta já está fechada e não pode ser alterada.')
            return redirect('comanda', pk=pk)
        if form.is_valid():
            item = form.save(commit=False)
            produto = item.prato or item.combo
            item.comanda = conta
            item.organizacao = org_atual(request)
            item.nome = produto.nome
            item.preco_unitario = produto.preco
            item.save()
            messages.success(request, 'Item adicionado à comanda.')
            return redirect('comanda', pk=pk)
    return render(request, 'cardapio/comanda.html', {'conta': conta, 'form': form})

@require_POST
@transaction.atomic
@login_required
def remover_item(request, pk, item_pk):
    conta = get_object_or_404(Comanda.objects.select_for_update().prefetch_related(Prefetch('itens', queryset=Item.objects.filter(organizacao=org_atual(request)))), pk=pk, organizacao=org_atual(request))
    if conta.aberta:
        get_object_or_404(Item, pk=item_pk, comanda=conta, organizacao=org_atual(request)).delete()
        messages.success(request, 'Item removido.')
    else:
        messages.error(request, 'Não é possível alterar uma conta fechada.')
    return redirect('comanda', pk=pk)

@transaction.atomic
@login_required
def fechar(request, pk):
    conta = get_object_or_404(Comanda.objects.select_for_update().prefetch_related(Prefetch('itens', queryset=Item.objects.filter(organizacao=org_atual(request)))), pk=pk, organizacao=org_atual(request))
    if not conta.aberta:
        return redirect('comanda', pk=pk)
    if request.method == 'POST':
        conta.total_fechado = conta.total
        conta.fechada_em = timezone.now()
        conta.save(update_fields=['total_fechado', 'fechada_em'])
        messages.success(request, 'Conta fechada. A mesa está livre para outro atendimento.')
        return redirect('comanda', pk=pk)
    return render(request, 'cardapio/fechar.html', {'conta': conta})

@login_required
def historico(request):
    return render(request, 'cardapio/historico.html', {'contas': Comanda.objects.filter(organizacao=org_atual(request), fechada_em__isnull=False).select_related('mesa')})

# Mesmo fluxo de ModelForm da Aula 5, reutilizado pelos três cadastros.
CADASTROS = {'pratos': (Prato, PratoForm, 'Pratos'), 'combos': (Combo, ComboForm, 'Combos'), 'mesas': (Mesa, MesaForm, 'Mesas')}

@login_required
def cadastro(request, tipo, pk=None):
    if tipo not in CADASTROS:
        raise Http404
    model, form_class, titulo = CADASTROS[tipo]
    objeto = get_object_or_404(model, pk=pk, organizacao=org_atual(request)) if pk else None
    form = form_class(request.POST if request.method == 'POST' else None, instance=objeto, org=org_atual(request))
    if request.method == 'POST' and form.is_valid():
        objeto = form.save(commit=False)
        objeto.organizacao = org_atual(request)
        objeto.save()
        form.save_m2m()
        messages.success(request, 'Cadastro salvo.')
        return redirect('cadastro', tipo=tipo)
    objetos = model.objects.filter(organizacao=org_atual(request))
    if tipo == 'pratos':
        objetos = filtrar_pratos(request, objetos)
    return render(request, 'cardapio/cadastro.html', {'form': form, 'objetos': objetos, 'categorias': Prato.Categoria.choices, 'titulo': titulo, 'tipo': tipo, 'editando': objeto})

@login_required
def excluir(request, tipo, pk):
    if tipo not in CADASTROS:
        raise Http404
    model, _, _ = CADASTROS[tipo]
    objeto = get_object_or_404(model, pk=pk, organizacao=org_atual(request))
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


@require_GET
def cardapio_publico(request, organizacao_id):
    """Catálogo público somente leitura, sempre restrito ao restaurante da URL."""
    from core.models import Organizacao
    org = get_object_or_404(Organizacao, pk=organizacao_id)
    pratos = list(Prato.objects.filter(organizacao=org, disponivel=True))
    combos = list(Combo.objects.filter(organizacao=org, disponivel=True)
                  .exclude(pratos__disponivel=False)
                  .exclude(pratos__isnull=True)
                  .exclude(pratos__in=Prato.objects.exclude(organizacao=org))
                  .prefetch_related(Prefetch('pratos', queryset=Prato.objects.filter(organizacao=org)))
                  .distinct())
    produtos = []
    for combo in combos:
        produtos.append({'key': f'combo-{combo.pk}', 'nome': combo.nome,
                         'descricao': combo.descricao, 'categoria': 'combos',
                         'categoria_nome': 'Combos da casa', 'preco': combo.preco,
                         'centavos': int(combo.preco * 100), 'arte': 'combo',
                         'componentes': ' + '.join(p.nome for p in combo.pratos.all())})
    artes = {'bebida': 'drink', 'sobremesa': 'dessert', 'acompanhamento': 'side', 'entrada': 'side'}
    for prato in pratos:
        produtos.append({'key': f'prato-{prato.pk}', 'nome': prato.nome,
                         'descricao': prato.descricao, 'categoria': prato.categoria,
                         'categoria_nome': prato.get_categoria_display(), 'preco': prato.preco,
                         'centavos': int(prato.preco * 100), 'arte': artes.get(prato.categoria, 'meal')})
    categorias = [('combos', 'Combos da casa')] + list(Prato.Categoria.choices)
    categorias = [(key, label) for key, label in categorias if any(p['categoria'] == key for p in produtos)]
    # Fallback sem JavaScript: busca e categorias continuam funcionando por GET.
    termo = request.GET.get('q', '').strip()
    categoria = request.GET.get('categoria', '')
    visiveis = [p for p in produtos if (not categoria or p['categoria'] == categoria)
                and (not termo or termo.casefold() in (p['nome'] + ' ' + p['descricao'] + ' ' + p.get('componentes', '')).casefold())]
    catalogo = [{'key': p['key'], 'nome': p['nome'], 'centavos': p['centavos']} for p in produtos]
    return render(request, 'cardapio/publico.html', {
        'organizacao': org, 'nome_restaurante': 'À Mesa' if org.nome == 'Organização padrão' else org.nome,
        'produtos': produtos, 'visiveis': visiveis, 'categorias': categorias, 'catalogo': catalogo,
        'termo': termo, 'categoria_atual': categoria,
    })
