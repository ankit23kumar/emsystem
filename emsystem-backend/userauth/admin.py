from django.contrib import admin
from .models import User
# Register your models here.

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        "full_name",
        "email",
        "created_at",
        "valid_until",
    )
    list_filter=('first_name','created_at',)
    search_fields = ("first_name","last_name","email",)
    ordering = ("first_name",)
    list_per_page = 25
    readonly_fields = ("created_at", "valid_until")
    
    @admin.display(description="Name", ordering="first_name")
    def full_name(self, obj):
            return f"{obj.first_name} {obj.last_name}"