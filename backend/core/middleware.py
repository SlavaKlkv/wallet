import json
import logging

from django.http import JsonResponse


class Custom404Middleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if response.status_code == 404 and request.path.startswith("/api/"):
            try:
                data = json.loads(response.content)
                if isinstance(data, dict) and "detail" in data:
                    return response
            except Exception as exc:
                logging.debug(
                    f"Custom404Middleware: Ошибка разбора json: {exc!r}")
            return JsonResponse({"detail": "Страница не найдена."}, status=404)
        return response
