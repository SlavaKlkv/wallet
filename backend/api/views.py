from django.db import transaction
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound
from rest_framework.response import Response

from wallets.models import Operation
from .serializers import OperationSerializer, WalletSerializer


class WalletViewSet(mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    serializer_class = WalletSerializer
    lookup_field = 'uuid'
    object = 'Кошелек'

    def get_object(self):
        obj = self.request.user.wallet
        uuid_from_url = str(self.kwargs.get('uuid'))
        if str(obj.uuid) != uuid_from_url:
            raise NotFound('Кошелек не найден.')
        return obj

    @action(
        detail=True,
        methods=('post',),
    )
    def operation(self, request, uuid=None):
        with (transaction.atomic()):
            wallet = self.get_object()
            wallet = wallet.__class__.objects.select_for_update(
                    ).get(pk=wallet.pk)

            serializer = OperationSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            operation_type = serializer.validated_data['operation_type']
            amount = serializer.validated_data['amount']

            if operation_type == Operation.WITHDRAW and \
                    wallet.balance < amount:
                return Response(
                    {'amount': ['Недостаточно средств.']},
                    status=status.HTTP_400_BAD_REQUEST
                )

            Operation.objects.create(
                wallet=wallet,
                operation_type=operation_type,
                amount=amount
            )

            wallet.refresh_from_db()

            return Response(
                WalletSerializer(wallet).data,
                status=status.HTTP_200_OK
            )
