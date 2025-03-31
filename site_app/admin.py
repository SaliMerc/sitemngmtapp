from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Transactions, Subscription,SubscriptionAmount

# Register the SubscriptionAmount model
@admin.register(SubscriptionAmount)
class TransactionsAdmin(admin.ModelAdmin):
    list_display = ('monthly_subscription_amount', 'yearly_subscription_amount')


# Register the Transactions model
@admin.register(Transactions)
class TransactionsAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone_number', 'amount', 'mpesa_code', 'checkout_id', 'status', 'timestamp')
    list_filter = ('status', 'timestamp')
    search_fields = ('phone_number', 'mpesa_code', 'checkout_id')
    readonly_fields = ('timestamp',)  # Make timestamp read-only

# Register the Subscription model
@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'subscription_type', 'start_date', 'end_date', 'is_active')
    list_filter = ('subscription_type', 'is_active')
    search_fields = ('user__username',)  # Search by username
    readonly_fields = ('end_date', 'is_active')  # Make end_date and is_active read-only

    # Customize the form to calculate end_date and is_active before saving
    def save_model(self, request, obj, form, change):
        obj.calculate_end_date()
        obj.check_active_status()
        super().save_model(request, obj, form, change)