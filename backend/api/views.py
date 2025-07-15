from django.db import transaction
from django.http import JsonResponse
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from core.mixins import CustomGetObjectMixin
from core.permissions import IsWalletOwner
from wallets.models import Operation, Wallet

from .serializers import OperationSerializer, WalletSerializer


class WalletViewSet(
    CustomGetObjectMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet
):
    serializer_class = WalletSerializer
    lookup_field = "uuid"
    permission_classes = (IsWalletOwner,)
    queryset = Wallet.objects.all()
    object = "Кошелек"

    @action(detail=True, methods=("post",))
    def operation(self, request, uuid=None):
        # В случае ошибки изменения не сохранятся
        with transaction.atomic():
            wallet = self.get_object()
            # Для предотвращения параллельных запросов
            # строка кошелька блокируется на уровне бд
            wallet = wallet.__class__.objects.select_for_update().get(
                pk=wallet.pk
            )

            serializer = OperationSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            operation_type = serializer.validated_data["operation_type"]
            amount = serializer.validated_data["amount"]

            if (
                operation_type == Operation.WITHDRAW
                and wallet.balance < amount
            ):
                return Response(
                    {"amount": ["Недостаточно средств."]},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            Operation.objects.create(
                wallet=wallet, operation_type=operation_type, amount=amount
            )

            wallet.refresh_from_db()

            return Response(
                WalletSerializer(wallet).data, status=status.HTTP_200_OK
            )


def healthcheck(request):
    return JsonResponse({"status": "OK"})
