from apps.custom_auth.infrastructure.api.v1.views.retired_legacy_identity_views import (
    RetiredLegacyIdentityRouteView,
)


retired_legacy_identity_view = RetiredLegacyIdentityRouteView.as_view()
