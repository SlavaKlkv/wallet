from rest_framework import serializers

from wallets.models import Operation, Wallet


class WalletSerializer(serializers.ModelSerializer):
    balance = serializers.FloatField()

    class Meta:
        model = Wallet
        fields = ("balance",)


class OperationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Operation
        fields = ("operation_type", "amount")
