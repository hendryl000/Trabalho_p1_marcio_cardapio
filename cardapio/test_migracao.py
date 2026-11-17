from django.db import connection
from django.db.migrations.executor import MigrationExecutor
from django.test import TransactionTestCase


class MigracaoOrganizacaoTests(TransactionTestCase):
    def test_preserva_dados_e_vincula_usuario_existente(self):
        executor = MigrationExecutor(connection)
        latest = executor.loader.graph.leaf_nodes()
        try:
            old_targets = [('cardapio', '0003_categorizar_pratos_demo'), ('core', None)]
            executor.migrate(old_targets)
            old = executor.loader.project_state([('cardapio', '0003_categorizar_pratos_demo'), ('auth', '0012_alter_user_first_name_max_length')]).apps
            user = old.get_model('auth', 'User').objects.create(username='usuario_legado')
            prato = old.get_model('cardapio', 'Prato').objects.create(nome='Prato legado', preco='22.50')
            combo = old.get_model('cardapio', 'Combo').objects.create(nome='Combo legado', preco='30.00')
            combo.pratos.add(prato)
            mesa = old.get_model('cardapio', 'Mesa').objects.create(numero=7)
            conta = old.get_model('cardapio', 'Comanda').objects.create(mesa=mesa)
            item = old.get_model('cardapio', 'Item').objects.create(comanda=conta, prato=prato, nome=prato.nome, preco_unitario=prato.preco)
            executor = MigrationExecutor(connection)
            executor.migrate(latest)
            apps = executor.loader.project_state(latest).apps
            org = apps.get_model('core', 'Organizacao').objects.get(nome='Organização padrão')
            for model, obj in [('Prato', prato), ('Combo', combo), ('Mesa', mesa), ('Comanda', conta), ('Item', item)]:
                migrated = apps.get_model('cardapio', model).objects.get(pk=obj.pk)
                self.assertEqual(migrated.organizacao_id, org.pk)
            self.assertEqual(apps.get_model('core', 'Perfil').objects.get(usuario_id=user.pk).organizacao_id, org.pk)
            self.assertEqual(apps.get_model('cardapio', 'Prato').objects.get(pk=prato.pk).nome, 'Prato legado')
            self.assertEqual(list(apps.get_model('cardapio', 'Combo').objects.get(pk=combo.pk).pratos.values_list('pk', flat=True)), [prato.pk])
        finally:
            MigrationExecutor(connection).migrate(latest)
