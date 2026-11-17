import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [('cardapio', '0005_preencher_organizacao')]
    operations = [
        migrations.AlterField(
            model_name=name, name='organizacao',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='core.organizacao'),
        )
        for name in ['prato', 'combo', 'mesa', 'comanda', 'item']
    ]
