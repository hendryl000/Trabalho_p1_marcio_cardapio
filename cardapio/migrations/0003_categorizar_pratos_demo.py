from django.db import migrations


def categorizar_pratos_demo(apps, schema_editor):
    Prato = apps.get_model('cardapio', 'Prato')
    categorias = {
        'Filé da casa': 'principal',
        'Frango grelhado': 'principal',
        'Risoto de cogumelos': 'principal',
        'Batata rústica': 'acompanhamento',
        'Suco de laranja': 'bebida',
        'Pudim artesanal': 'sobremesa',
    }
    for nome, categoria in categorias.items():
        Prato.objects.using(schema_editor.connection.alias).filter(
            nome=nome, categoria='outros',
        ).update(categoria=categoria)


class Migration(migrations.Migration):
    dependencies = [('cardapio', '0002_prato_categoria')]

    operations = [
        migrations.RunPython(categorizar_pratos_demo, migrations.RunPython.noop),
    ]
