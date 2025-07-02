from rest_framework import viewsets

from core.mixins import CustomGetObjectMixin


class WalletViewSet(CustomGetObjectMixin, viewsets.ReadOnlyModelViewSet):
    object = "Кошелек"
