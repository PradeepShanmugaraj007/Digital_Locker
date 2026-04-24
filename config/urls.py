"""Root URL configuration."""
from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

urlpatterns = [
    # Django admin
    path("admin/", admin.site.urls),

    # API routes
    path("api/auth/", include("apps.accounts.urls")),
    path("api/lockers/", include("apps.lockers.urls")),
    path("api/reservations/", include("apps.reservations.urls")),

    # OpenAPI schema & docs
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/schema/swagger-ui/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("api/schema/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
]
