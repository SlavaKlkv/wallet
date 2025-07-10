from django.contrib import admin

from .models import User


admin.site.empty_value_display = "Не указано"


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        "username",
        "first_name",
        "last_name",
        "email",
        "is_staff"
    )
    search_fields = ("username", "email")
    ordering = ("username",)
