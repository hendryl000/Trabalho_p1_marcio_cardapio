from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.db import connection
from django.test import Client
from django.test.utils import CaptureQueriesContext
from cardapio.models import Comanda


class Command(BaseCommand):
    help = 'Mede consultas das telas reais, incluindo autenticação e renderização.'

    def add_arguments(self, parser):
        parser.add_argument('--usuario', required=True)

    def handle(self, *args, **options):
        try:
            user = get_user_model().objects.select_related('perfil__organizacao').get(username=options['usuario'])
            org = user.perfil.organizacao
        except (get_user_model().DoesNotExist, AttributeError):
            raise CommandError('Informe um usuário com Perfil.')
        client = Client()
        client.force_login(user)
        urls = ['/', '/cardapio/', '/historico/', '/dashboard/', '/api/dashboard/', f'/menu/{org.pk}/']
        conta = Comanda.objects.filter(organizacao=org).first()
        if conta:
            urls.append(f'/comandas/{conta.pk}/')
        if user.perfil.eh_admin:
            urls.append('/dashboard/exportar.csv')
        try:
            for url in urls:
                with CaptureQueriesContext(connection) as queries:
                    response = client.get(url)
                    if response.streaming:
                        for _ in response.streaming_content:
                            pass
                self.stdout.write(f'{url}: HTTP {response.status_code}; {len(queries)} consultas')
        finally:
            client.logout()
