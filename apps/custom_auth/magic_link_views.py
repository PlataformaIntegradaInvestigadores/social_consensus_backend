from django.http import JsonResponse


def _retired_magic_link_response(_request, *args, **kwargs):
    return JsonResponse(
        {
            "detail": (
                "Magic link legacy fue retirado del backend social. "
                "Use profile_identity_backend para autenticacion canonica."
            ),
            "canonical_service": "profile_identity_backend",
        },
        status=410,
    )


magic_link_login_page = _retired_magic_link_response
generate_magic_link = _retired_magic_link_response
verify_magic_link = _retired_magic_link_response
test_users_list = _retired_magic_link_response
quick_login = _retired_magic_link_response
