from http import HTTPStatus
import threading

import pytest

from core.constants import (
    WALLET_DETAIL_URL,
    WALLET_OPERATION_URL,
)
from logging_setup import logger_setup


logger = logger_setup()


def assert_response_and_balance(response, wallet, url, expected_balance):
    """
    Проверки статус-кода и наличия поля в ответе, его значения и баланса из бд.
    """
    assert (
        response.status_code == HTTPStatus.OK
    ), f"POST {url} должен возвращать 200, а вернул {response.status_code}"

    assert 'balance' in response.data, \
        "В ответе должно присутствовать поле 'balance'"

    # Сравнение со значением в ответе API
    assert response.data.get('balance') == expected_balance, (
        f"Баланс должен быть {expected_balance}, "
        f"а вернулся {response.data.get('balance')}"
    )

    wallet.refresh_from_db()
    # Сравнение с балансом в базе
    assert (
        float(wallet.balance) == expected_balance
    ), (
        f"Баланс в базе должен быть {expected_balance}, "
        f"а получен {wallet.balance}"
    )


@pytest.mark.django_db(transaction=True)
class TestWallets:

    def test_wallet_detail_available(self, auth_client, wallet):
        """Пользователь может получить баланс своего кошелька."""
        url = WALLET_DETAIL_URL.format(uuid=wallet.uuid)
        response = auth_client.get(url)

        assert (
            response.status_code == HTTPStatus.OK
        ), f"GET {url} должен возвращать 200, а вернул {response.status_code}"

        assert 'balance' in response.data, \
            "В ответе должно присутствовать поле 'balance'"

        assert response.data.get('balance') == wallet.balance, (
            f"Баланс должен быть {wallet.balance}, "
            f"а вернулся {response.data.get('balance')}"
        )

    @pytest.mark.parametrize("operation_type, amount, expected_balance", [
        ("deposit", 1000, 1000),
        ("withdraw", 1000, 0),
    ])
    def test_wallet_operation(
            self,
            auth_client,
            make_deposit,
            wallet,
            operation_type,
            amount,
            expected_balance,
    ):
        """
        Пользователь может пополнить свой кошелек и снять с него средства.
        """
        url = WALLET_OPERATION_URL.format(uuid=wallet.uuid)

        if operation_type == "withdraw":
            make_deposit(wallet, amount)

        response = auth_client.post(url, {
            "operation_type": operation_type,
            "amount": amount
        })

        assert_response_and_balance(response, wallet, url, expected_balance)

    def test_wallet_parallel_operations(self, auth_client, wallet,
                                        make_deposit):
        """Операции корректно работают при параллельных запросах."""

        url = WALLET_OPERATION_URL.format(uuid=wallet.uuid)

        initial_deposit = 1000
        make_deposit(wallet, initial_deposit)
        wallet.refresh_from_db()
        assert wallet.balance == initial_deposit

        def withdraw():
            auth_client.post(url, {
                "operation_type": "withdraw",
                "amount": 500
            })

        def deposit():
            auth_client.post(url, {
                "operation_type": "deposit",
                "amount": 500
            })

        # Запуск двух параллельных потоков
        t1 = threading.Thread(target=withdraw)
        t2 = threading.Thread(target=deposit)
        t1.start()
        t2.start()
        t1.join()
        t2.join()

        wallet.refresh_from_db()

        assert wallet.balance == initial_deposit, (
            "Баланс после параллельных операций "
            f"должен быть {initial_deposit}, "
            f"а получен {wallet.balance}"
        )

    def test_wallet_multiple_deposits_and_withdraws(self, auth_client, wallet,
                                                    make_deposit):
        """Корректно выполняется несколько операций подряд в одном потоке."""
        deposit_count = 3
        withdraw_count = 2
        deposit_amount = 100
        withdraw_amount = 50

        url = WALLET_OPERATION_URL.format(uuid=wallet.uuid)

        for _ in range(deposit_count):
            auth_client.post(url, {
                "operation_type": "deposit", "amount": deposit_amount
            })
        for _ in range(withdraw_count):
            auth_client.post(url, {
                "operation_type": "withdraw", "amount": withdraw_amount
            })

        wallet.refresh_from_db()
        result_balance = (deposit_count * deposit_amount
                          - withdraw_count * withdraw_amount)

        assert (
            wallet.balance == result_balance
        ), (
            f"Баланс должен быть {result_balance}, а получен {wallet.balance}"
        )

    def test_wallet_decimal_operations(self, auth_client, wallet,
                                       make_deposit):
        """
        Корректно работают операции с дробными суммами.
        """
        deposit_amount = 1000
        decimal_amount = 100.55

        url = WALLET_OPERATION_URL.format(uuid=wallet.uuid)

        make_deposit(wallet, deposit_amount)
        response = auth_client.post(url, {
            "operation_type": "deposit",
            "amount": decimal_amount
        })
        expected_balance = deposit_amount + decimal_amount
        assert_response_and_balance(response, wallet, url, expected_balance)

    def test_wallet_min_amount(self, auth_client, wallet, make_deposit):
        """
        Корректно работает операция с минимальной допустимой суммой.
        """
        deposit_amount = 1
        min_amount = 0.01

        url = WALLET_OPERATION_URL.format(uuid=wallet.uuid)

        make_deposit(wallet, deposit_amount)
        response = auth_client.post(url, {
            "operation_type": "withdraw",
            "amount": min_amount
        })
        expected_balance = deposit_amount - min_amount
        assert_response_and_balance(response, wallet, url, expected_balance)
