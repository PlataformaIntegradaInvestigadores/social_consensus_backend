from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response


def _retired_user_embedding_response(request):
    return Response(
        {
            "detail": (
                "Los embeddings y preferencias de investigadores fueron retirados "
                "del backend social. Use profile_identity_backend como fuente "
                "canonica de identidad/perfil."
            ),
            "canonical_service": "profile_identity_backend",
        },
        status=status.HTTP_410_GONE,
    )


@api_view(["POST"])
@permission_classes([AllowAny])
def update_user_job_embedding(request):
    return _retired_user_embedding_response(request)


@api_view(["POST"])
@permission_classes([AllowAny])
def update_user_feed_embedding(request):
    return _retired_user_embedding_response(request)


@api_view(["POST"])
@permission_classes([AllowAny])
def update_all_user_embeddings(request):
    return _retired_user_embedding_response(request)


@api_view(["GET"])
@permission_classes([AllowAny])
def get_user_embedding_status(request):
    return _retired_user_embedding_response(request)


@api_view(["POST"])
@permission_classes([AllowAny])
def update_user_interests(request):
    return _retired_user_embedding_response(request)
