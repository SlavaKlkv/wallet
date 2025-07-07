import pytest

from wallets.models import Operation, Wallet


def _make_operation(wallet, amount, operation_type):
    return Operation.objects.create(
        wallet=wallet,
        operation_type=operation_type,
        amount=amount,
    )


@pytest.fixture
def wallet(user):
    return Wallet.objects.create(user=user)


@pytest.fixture
def make_deposit():
    def _make(wallet, amount):
        return _make_operation(wallet, amount, Operation.DEPOSIT)
    return _make


@pytest.fixture
def make_withdraw():
    def _make(wallet, amount):
        return _make_operation(wallet, amount, Operation.WITHDRAW)
    return _make
