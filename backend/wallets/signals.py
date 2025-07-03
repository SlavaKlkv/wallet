from django.db.models import Sum
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from .models import Operation


@receiver([post_save, post_delete], sender=Operation)
def update_wallet_balance(sender, instance, **kwargs):
    wallet = instance.wallet
    total_deposit = wallet.operations.filter(
        operation_type=Operation.DEPOSIT
    ).aggregate(total=Sum('amount'))['total'] or 0

    total_withdraw = wallet.operations.filter(
        operation_type=Operation.WITHDRAW
    ).aggregate(total=Sum('amount'))['total'] or 0

    wallet.balance = total_deposit - total_withdraw
    wallet.save(update_fields=['balance'])