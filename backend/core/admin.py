"""
Django admin configuration for core models.
"""
from django.contrib import admin
from .models import Dataset, DatasetColumn


@admin.register(Dataset)
class DatasetAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'status', 'row_count', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['name', 'slug', 'original_filename']
    readonly_fields = ['id', 'slug', 'table_name', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('id', 'name', 'slug', 'api_key')
        }),
        ('File Information', {
            'fields': ('original_filename', 'file', 'file_size')
        }),
        ('Processing Status', {
            'fields': ('status', 'error_message', 'row_count', 'table_name')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )


@admin.register(DatasetColumn)
class DatasetColumnAdmin(admin.ModelAdmin):
    list_display = ['dataset', 'name', 'field_name', 'data_type', 'nullable', 'position']
    list_filter = ['data_type', 'nullable', 'unique']
    search_fields = ['name', 'field_name', 'dataset__name']
    ordering = ['dataset', 'position']
