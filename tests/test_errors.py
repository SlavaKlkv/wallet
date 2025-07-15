from http import HTTPStatus

import pytest

from core.constants import WALLET_DETAIL_URL, WALLET_OPERATION_URL


NOT_EXIST_UUID = "00000000-0000-0000-0000-000000000404"
DRF_INVALID_CHOICE = "нет среди допустимых вариантов"


@pytest.mark.django_db()
class TestWalletsErrors:

    @pytest.mark.parametrize(
        "client_fixture, method, url, payload, expected_status, not_found",
        [
            # GET detail (401, 403, 404)
            (
                "client",
                "get",
                WALLET_DETAIL_URL,
                None,
                HTTPStatus.UNAUTHORIZED,
                False,
            ),
            (
                "auth_client_2",
                "get",
                WALLET_DETAIL_URL,
                None,
                HTTPStatus.FORBIDDEN,
                False,
            ),
            (
                "auth_client",
                "get",
                WALLET_DETAIL_URL,
                None,
                HTTPStatus.NOT_FOUND,
                True,
            ),
            # POST deposit (401, 403, 404)
            (
                "client",
                "post",
                WALLET_OPERATION_URL,
                {"operation_type": "deposit", "amount": "100"},
                HTTPStatus.UNAUTHORIZED,
                False,
            ),
            (
                "auth_client_2",
                "post",
                WALLET_OPERATION_URL,
                {"operation_type": "deposit", "amount": "100"},
                HTTPStatus.FORBIDDEN,
                False,
            ),
            (
                "auth_client",
                "post",
                WALLET_OPERATION_URL,
                {"operation_type": "deposit", "amount": "100"},
                HTTPStatus.NOT_FOUND,
                True,
            ),
            # POST withdraw (401, 403, 404)
            (
                "client",
                "post",
                WALLET_OPERATION_URL,
                {"operation_type": "withdraw", "amount": "50"},
                HTTPStatus.UNAUTHORIZED,
                False,
            ),
            (
                "auth_client_2",
                "post",
                WALLET_OPERATION_URL,
                {"operation_type": "withdraw", "amount": "50"},
                HTTPStatus.FORBIDDEN,
                False,
            ),
            (
                "auth_client",
                "post",
                WALLET_OPERATION_URL,
                {"operation_type": "withdraw", "amount": "50"},
                HTTPStatus.NOT_FOUND,
                True,
            ),
        ],
    )
    def test_wallet_access_permissions(
        self,
        request,
        wallet,
        client_fixture,
        method,
        url,
        payload,
        expected_status,
        not_found,
    ):
        """Корректно работают коды ответов с разными параметрами."""
        uuid = NOT_EXIST_UUID if not_found else wallet.uuid
        url = url.format(uuid=uuid)
        client_method = getattr(
            request.getfixturevalue(client_fixture), method
        )
        if payload:
            response = client_method(url, payload)
        else:
            response = client_method(url)

        assert response.status_code == expected_status, (
            f"{method.upper()} {url} для клиента {client_fixture} "
            f"должен возвращать {expected_status}, "
            f"а вернул {response.status_code}"
        )
        assert (
            "detail" in response.data
        ), "Ответ должен содержать ключ 'detail'"

    @pytest.mark.parametrize(
        "payload, expected_error_field, expected_message",
        [
            # Нет amount
            ({"operation_type": "deposit"}, "amount", "Обязательное поле."),
            # Нет operation_type
            ({"amount": "10"}, "operation_type", "Обязательное поле."),
            # Некорректный тип операции
            (
                {"operation_type": "wrong", "amount": "10"},
                "operation_type",
                "Некорректный тип операции.",
            ),
            # Сумма меньше минимума
            (
                {"operation_type": "deposit", "amount": "0"},
                "amount",
                "Убедитесь, что это значение больше либо равно",
            ),
            # Отрицательные значение
            (
                {"operation_type": "withdraw", "amount": "-1"},
                "amount",
                "Убедитесь, что это значение больше либо равно",
            ),
        ],
    )
    def test_wallet_operations_bad_request(
        self,
        auth_client,
        wallet,
        payload,
        expected_error_field,
        expected_message,
    ):
        """
        POST-запросы с некорректными данными
        возвращают 400 и сообщение об ошибке.
        """
        url = WALLET_OPERATION_URL.format(uuid=wallet.uuid)
        response = auth_client.post(url, payload)
        assert response.status_code == HTTPStatus.BAD_REQUEST
        assert expected_error_field in response.data
        # Сообщение может быть как строкой, так и списком ошибок
        messages = response.data.get(expected_error_field)
        if isinstance(messages, list):
            assert any(
                expected_message in str(m) or DRF_INVALID_CHOICE in str(m)
                for m in messages
            ), (
                f"Сообщение об ошибке должно содержать '{expected_message}' "
                f"или '{DRF_INVALID_CHOICE}'. Было: {messages}"
            )
        else:
            assert expected_message in str(
                messages
            ) or DRF_INVALID_CHOICE in str(messages), (
                f"Сообщение об ошибке должно содержать '{expected_message}' "
                f"или '{DRF_INVALID_CHOICE}'. Было: {messages}"
            )
