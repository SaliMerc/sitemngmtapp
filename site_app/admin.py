from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Transactions,SubscriptionAmount

# Register the SubscriptionAmount model
@admin.register(SubscriptionAmount)
class TransactionsAdmin(admin.ModelAdmin):
    list_display = ('monthly_subscription_amount', 'yearly_subscription_amount')


# Register the Transactions model
@admin.register(Transactions)
class TransactionsAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone_number', 'amount', 'mpesa_code', 'checkout_id', 'status', 'start_date')
    list_filter = ('status', 'start_date')
    search_fields = ('phone_number', 'mpesa_code', 'checkout_id')
    readonly_fields = ('start_date',)  # Make timestamp read-only