import uuid
from decimal import Decimal

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models

from core.constants import (
    AMOUNT_MIN_VALUE,
    MONEY_DECIMAL_PLACES,
    MONEY_DEFAULT,
    MONEY_MAX_DIGITS,
    OPERATION_TYPE_MAX_LENGTH,
)


class Wallet(models.Model):
    uuid = models.UUIDField(
        unique=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name='UUID'
    )
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='wallet',
        verbose_name='Владелец',
        help_text='Пользователь, владеющий кошельком'
    )
    balance = models.DecimalField(
        max_digits=MONEY_MAX_DIGITS,
        decimal_places=MONEY_DECIMAL_PLACES,
        default=MONEY_DEFAULT,
        verbose_name='Баланс'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Дата обновления'
    )

    class Meta:
        verbose_name = "Кошелек"
        verbose_name_plural = "Кошельки"
        ordering = ('-created_at',)

    def __str__(self):
        return f"Кошелек {str(self.uuid)[:8]}"


class Operation(models.Model):
    DEPOSIT = 'deposit'
    WITHDRAW = 'withdraw'
    OPERATION_TYPE_CHOICES = (
        (DEPOSIT, 'Пополнение'),
        (WITHDRAW, 'Снятие'),
    )

    wallet = models.ForeignKey(
        Wallet,
        on_delete=models.CASCADE,
        related_name='operations',
        verbose_name='Кошелёк',
        blank=False,
        null=False,
        help_text='Кошелёк, к которому относится операция'
    )
    operation_type = models.CharField(
        max_length=OPERATION_TYPE_MAX_LENGTH,
        choices=OPERATION_TYPE_CHOICES,
        verbose_name='Тип операции',
        help_text='Тип операции: пополнение или снятие'
    )
    amount = models.DecimalField(
        max_digits=MONEY_MAX_DIGITS,
        decimal_places=MONEY_DECIMAL_PLACES,
        verbose_name='Сумма',
        help_text='Сумма операции',
        validators=[MinValueValidator(Decimal(str(AMOUNT_MIN_VALUE)))],
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Время операции',
        help_text='Время проведения операции'
    )

    class Meta:
        verbose_name = "Операция"
        verbose_name_plural = "Операции"
        ordering = ('-created_at',)

    def clean(self):
        if self.operation_type == self.WITHDRAW:
            wallet = Wallet.objects.get(pk=self.wallet.pk)
            if wallet.balance < self.amount:
                raise ValidationError('Недостаточно средств.')

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return (
            f"{self.get_operation_type_display()} на сумму {self.amount} "
            f"от {self.created_at.strftime('%Y-%m-%d %H:%M:%S')}"
        )
