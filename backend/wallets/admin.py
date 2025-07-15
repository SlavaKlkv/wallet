from django.contrib import admin

from .models import Operation, Wallet


admin.site.empty_value_display = "Не указано"


class OperationInline(admin.TabularInline):
    model = Operation
    extra = 0


@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):
    list_display = (
        "uuid",
        "user",
        "balance",
        "created_at",
        "updated_at",
    )
    readonly_fields = ("balance",)
    search_fields = ("uuid", "user__username", "user__email")
    list_filter = ("user", "created_at")
    raw_id_fields = ("user",)
    inlines = [OperationInline]


@admin.register(Operation)
class OperationAdmin(admin.ModelAdmin):
    list_display = ("id", "wallet", "operation_type", "amount", "created_at")
