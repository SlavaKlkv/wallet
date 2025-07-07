from django.contrib import admin

from .models import User, Wallet


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


@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):
    list_display = (
        'uuid',
        'user',
        'balance',
        'created_at',
        'updated_at',
    )
    search_fields = (
        'uuid',
        'user__username',
        'user__email'
    )
    list_filter = ('user', 'created_at')
    raw_id_fields = ('user',)
