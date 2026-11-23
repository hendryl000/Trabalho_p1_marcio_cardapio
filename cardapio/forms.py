from django import forms
from .models import Prato, Combo, Mesa, Item

class FormDaOrganizacao(forms.ModelForm):
    def __init__(self, *args, org=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.org = org
        self.instance.organizacao = org


class PratoForm(FormDaOrganizacao):
    class Meta:
        model = Prato
        fields = ['nome', 'descricao', 'categoria', 'preco', 'disponivel']

    def clean_preco(self):
        preco = self.cleaned_data.get('preco')
        if preco is not None and preco <= 0:
            raise forms.ValidationError('O preço do prato deve ser maior que zero.')
        return preco

class ComboForm(FormDaOrganizacao):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['pratos'].queryset = Prato.objects.filter(organizacao=self.org)

    class Meta:
        model = Combo
        fields = ['nome', 'descricao', 'pratos', 'preco', 'disponivel']
        widgets = {'pratos': forms.CheckboxSelectMultiple}

class MesaForm(FormDaOrganizacao):
    def clean_numero(self):
        numero = self.cleaned_data['numero']
        duplicados = Mesa.objects.filter(organizacao=self.org, numero=numero)
        if self.instance.pk:
            duplicados = duplicados.exclude(pk=self.instance.pk)
        if duplicados.exists():
            raise forms.ValidationError('Já existe uma mesa com este número na sua organização.')
        return numero

    class Meta:
        model = Mesa
        fields = ['numero', 'capacidade']

class ItemForm(FormDaOrganizacao):
    class Meta:
        model = Item
        fields = ['prato', 'combo', 'quantidade', 'observacao']
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['prato'].queryset = Prato.objects.filter(organizacao=self.org, disponivel=True)
        self.fields['combo'].queryset = Combo.objects.filter(organizacao=self.org, disponivel=True).exclude(pratos__disponivel=False).distinct()
    def clean(self):
        data = super().clean()
        if bool(data.get('prato')) == bool(data.get('combo')):
            raise forms.ValidationError('Selecione um prato OU um combo por item.')
        return data


class PeriodoForm(forms.Form):
    inicio = forms.DateField(label='De', required=False, input_formats=['%Y-%m-%d'],
                             widget=forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'))
    fim = forms.DateField(label='Até', required=False, input_formats=['%Y-%m-%d'],
                          widget=forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'))

    def clean(self):
        data = super().clean()
        inicio, fim = data.get('inicio'), data.get('fim')
        if inicio and fim and inicio > fim:
            raise forms.ValidationError('A data inicial não pode ser posterior à data final.')
        for campo in ['inicio', 'fim']:
            valor = data.get(campo)
            if valor and not 1900 <= valor.year <= 9998:
                self.add_error(campo, 'Informe uma data entre 1900 e 9998.')
        return data
