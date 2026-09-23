from django import forms
from .models import Prato, Combo, Mesa, Item

class PratoForm(forms.ModelForm):
    class Meta:
        model = Prato
        fields = ['nome', 'descricao', 'preco', 'disponivel']

class ComboForm(forms.ModelForm):
    class Meta:
        model = Combo
        fields = ['nome', 'descricao', 'pratos', 'preco', 'disponivel']
        widgets = {'pratos': forms.CheckboxSelectMultiple}

class MesaForm(forms.ModelForm):
    class Meta:
        model = Mesa
        fields = ['numero', 'capacidade']

class ItemForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = ['prato', 'combo', 'quantidade', 'observacao']
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['prato'].queryset = Prato.objects.filter(disponivel=True)
        self.fields['combo'].queryset = Combo.objects.filter(disponivel=True).exclude(pratos__disponivel=False).distinct()
    def clean(self):
        data = super().clean()
        if bool(data.get('prato')) == bool(data.get('combo')):
            raise forms.ValidationError('Selecione um prato OU um combo por item.')
        return data
