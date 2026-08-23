"""Поведение кошелька под параллельной нагрузкой.

Ради этих тестов в проекте и стоят `select_for_update()` и пересчёт баланса
из журнала операций. Без них они падают — что и требуется от регрессии.
"""

from concurrent.futures import ThreadPoolExecutor
from decimal import Decimal
from http import HTTPStatus

from django.db import connections
import pytest

from core.constants import WALLET_OPERATION_URL


pytestmark = [
    pytest.mark.django_db(transaction=True),
    pytest.mark.usefixtures("requires_row_locks"),
]


def _post_operation(client, url, operation_type, amount):
    """Один запрос из отдельного потока.

    Django открывает соединение на поток и не закрывает его сам, поэтому
    соединение закрывается вручную — иначе тестовая БД не дропнется.
    """
    try:
        return client.post(
            url, {"operation_type": operation_type, "amount": amount}
        ).status_code
    finally:
        connections.close_all()


def _run_parallel(fn, times):
    with ThreadPoolExecutor(max_workers=times) as pool:
        return list(pool.map(lambda _: fn(), range(times)))


class TestConcurrency:

    def test_parallel_withdrawals_never_overdraw(
        self, auth_client, wallet, make_deposit
    ):
        """Десять одновременных снятий по 200 при балансе 1000.

        Успешными должны оказаться ровно пять: проверка средств и списание
        происходят под блокировкой строки, поэтому уйти в минус нельзя.
        """
        make_deposit(wallet, 1000)
        url = WALLET_OPERATION_URL.format(uuid=wallet.uuid)

        statuses = _run_parallel(
            lambda: _post_operation(auth_client, url, "withdraw", 200), 10
        )

        assert statuses.count(HTTPStatus.OK) == 5, (
            "Успешных снятий должно быть ровно пять, "
            f"а получилось {statuses.count(HTTPStatus.OK)}"
        )

        wallet.refresh_from_db()
        assert wallet.balance == Decimal("0.00")
        assert wallet.balance >= 0, "Баланс не может стать отрицательным"

    def test_parallel_deposits_are_all_counted(self, auth_client, wallet):
        """Двадцать одновременных пополнений — ни одно не потеряно."""
        url = WALLET_OPERATION_URL.format(uuid=wallet.uuid)

        _run_parallel(
            lambda: _post_operation(auth_client, url, "deposit", 50), 20
        )

        wallet.refresh_from_db()
        assert wallet.balance == Decimal("1000.00")
        assert wallet.operations.count() == 20

    def test_mixed_operations_settle_exactly(
        self, auth_client, wallet, make_deposit
    ):
        """Десять пополнений и десять снятий по 100 вперемешку.

        Средств хватает на любое снятие, поэтому все двадцать запросов должны
        пройти, а баланс — вернуться к исходному: ни одна операция не
        потерялась и ни одна не применилась дважды.
        """
        make_deposit(wallet, 2000)
        url = WALLET_OPERATION_URL.format(uuid=wallet.uuid)

        operations = ["deposit", "withdraw"] * 10

        with ThreadPoolExecutor(max_workers=10) as pool:
            statuses = list(
                pool.map(
                    lambda op: _post_operation(auth_client, url, op, 100),
                    operations,
                )
            )

        assert statuses.count(HTTPStatus.OK) == 20

        wallet.refresh_from_db()
        assert wallet.balance == Decimal("2000.00")
        # исходное пополнение плюс двадцать операций
        assert wallet.operations.count() == 21
