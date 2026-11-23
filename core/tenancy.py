from django.core.exceptions import PermissionDenied
from .models import Perfil


def perfil_atual(request):
    if not request.user.is_authenticated:
        raise PermissionDenied('Entre para acessar sua organização.')
    if not hasattr(request, '_perfil_atual'):
        try:
            request._perfil_atual = Perfil.objects.select_related('organizacao').get(usuario=request.user)
        except Perfil.DoesNotExist:
            raise PermissionDenied('Usuário sem organização. Solicite um perfil ao administrador.')
        # Compartilha o resultado com templates e evita consultas repetidas.
        request.user._state.fields_cache['perfil'] = request._perfil_atual
    return request._perfil_atual


def org_atual(request):
    return perfil_atual(request).organizacao
