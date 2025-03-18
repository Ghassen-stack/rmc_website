from django.contrib import admin
from .models import Product, TeamMember

admin.site.register(Product)
admin.site.register(TeamMember)
from .models import Order  # Import the Order model

# Register the Order model
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'total', 'status', 'created_at', 'location', 'estimated_delivery_time')
    list_filter = ('status', 'created_at')
    search_fields = ('user__username', 'id')
    list_editable = ('status', 'location', 'estimated_delivery_time')  # Make these fields editable directly in the list view
    readonly_fields = ('created_at',)  # Make created_at read-only