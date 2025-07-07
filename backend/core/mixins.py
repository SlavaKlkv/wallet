from django.http import Http404
from rest_framework.exceptions import NotFound


class CustomGetObjectMixin:
    object = "Объект"

    @property
    def not_found_detail(self):
        return f"{self.object} не найден."

    def get_object(self):
        try:
            return super().get_object()
        except Http404:
            raise NotFound(detail=self.not_found_detail)
