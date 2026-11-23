from django.db import migrations


def promover_superusuarios(apps, schema_editor):
    Perfil = apps.get_model('core', 'Perfil')
    Perfil.objects.using(schema_editor.connection.alias).filter(usuario__is_superuser=True).update(papel='admin')


class Migration(migrations.Migration):
    dependencies = [('core', '0002_perfil_papel')]
    operations = [migrations.RunPython(promover_superusuarios, migrations.RunPython.noop)]
