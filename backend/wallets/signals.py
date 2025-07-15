from django.db.models import Sum
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from .models import Operation


@receiver([post_save, post_delete], sender=Operation)
def update_wallet_balance(sender, instance, **kwargs):
    wallet = instance.wallet

    totals = {
        operation_type: wallet.operations.filter(
            operation_type=operation_type
        ).aggregate(total=Sum("amount"))["total"]
        or 0
        for operation_type in (Operation.DEPOSIT, Operation.WITHDRAW)
    }

    wallet.balance = totals.get(Operation.DEPOSIT) - totals.get(
        Operation.WITHDRAW
    )
    wallet.save(update_fields=["balance"])
