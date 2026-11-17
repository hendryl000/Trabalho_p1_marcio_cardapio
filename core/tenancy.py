from django.core.exceptions import PermissionDenied
from .models import Perfil


def org_atual(request):
    if not request.user.is_authenticated:
        raise PermissionDenied('Entre para acessar sua organização.')
    try:
        return request.user.perfil.organizacao
    except Perfil.DoesNotExist:
        raise PermissionDenied('Usuário sem organização. Solicite um perfil ao administrador.')
