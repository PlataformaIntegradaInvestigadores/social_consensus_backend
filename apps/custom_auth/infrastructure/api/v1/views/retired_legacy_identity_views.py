from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView


class RetiredLegacyIdentityRouteView(APIView):
    authentication_classes = []
    permission_classes = [permissions.AllowAny]

    def dispatch(self, request, *args, **kwargs):
        self.legacy_route = kwargs.pop("legacy_route", "")
        return super().dispatch(request, *args, **kwargs)

    def _response(self, request, *args, **kwargs):
        return Response(
            {
                "detail": (
                    "Esta ruta legacy de identidad, perfil o grupos fue retirada "
                    "del backend social. Use el gateway para consumir "
                    "profile_identity_backend como fuente canonica."
                ),
                "canonical_service": "profile_identity_backend",
                "gateway_base_path": "/api/",
                "legacy_route": self.legacy_route or request.path,
            },
            status=status.HTTP_410_GONE,
        )

    get = _response
    post = _response
    put = _response
    patch = _response
    delete = _response
    options = _response
