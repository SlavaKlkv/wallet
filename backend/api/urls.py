from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.views import WalletViewSet, healthcheck


app_name = "api"

router_v1 = DefaultRouter()
router_v1.register("wallets", WalletViewSet, basename="wallets")

urlpatterns_v1 = [
    path(
        "v1/",
        include(
            [
                path("", include(router_v1.urls)),
                path("auth/", include("djoser.urls")),
                path("auth/", include("djoser.urls.authtoken")),
                path("health", healthcheck),
            ]
        ),
    ),
]

urlpatterns = urlpatterns_v1
