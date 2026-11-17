from django.conf import settings
from django.db import migrations


def preencher(apps, schema_editor):
    alias = schema_editor.connection.alias
    Org = apps.get_model('core', 'Organizacao')
    Perfil = apps.get_model('core', 'Perfil')
    User = apps.get_model(settings.AUTH_USER_MODEL)
    org, _ = Org.objects.using(alias).get_or_create(nome='Organização padrão')
    for name in ['Prato', 'Combo', 'Mesa', 'Comanda', 'Item']:
        apps.get_model('cardapio', name).objects.using(alias).filter(
            organizacao__isnull=True
        ).update(organizacao_id=org.pk)
    # Usuários anteriores pertencem à instalação única da P1.
    for user_id in User.objects.using(alias).values_list('pk', flat=True):
        Perfil.objects.using(alias).get_or_create(usuario_id=user_id, defaults={'organizacao_id': org.pk})


class Migration(migrations.Migration):
    dependencies = [
        ('cardapio', '0004_comanda_organizacao_combo_organizacao_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]
    operations = [migrations.RunPython(preencher, migrations.RunPython.noop)]
