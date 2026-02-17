"""
Django admin for API keys.
"""
from django.contrib import admin
from .models import APIKey


@admin.register(APIKey)
class APIKeyAdmin(admin.ModelAdmin):
    list_display = ['name', 'prefix', 'is_active', 'created_at', 'last_used']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'prefix']
    readonly_fields = ['id', 'prefix', 'hashed_key', 'created_at', 'last_used']
    
    fieldsets = (
        ('Key Information', {
            'fields': ('id', 'name', 'prefix', 'hashed_key', 'is_active')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'last_used')
        }),
    )
