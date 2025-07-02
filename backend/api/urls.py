from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.views import WalletViewSet

app_name = "api"

router_v1 = DefaultRouter()
routes = [
    ("wallets", WalletViewSet),
]
for prefix, viewset in routes:
    router_v1.register(prefix, viewset, basename=prefix)

urlpatterns_v1 = [
    path(
        "v1/",
        include([
            path("", include(router_v1.urls)),
            path("auth/", include("djoser.urls")),
            path("auth/", include("djoser.urls.authtoken")),
        ]),
    ),
]

urlpatterns = urlpatterns_v1

