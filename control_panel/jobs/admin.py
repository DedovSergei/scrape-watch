from django.contrib import admin
from .models import ScrapeJob

@admin.register(ScrapeJob)
class ScrapeJobAdmin(admin.ModelAdmin):
    # Fields that will be displayed in the list 
    list_display = ('name', 'user', 'is_active', 'target_url', 'last_scraped')

    # Adds a filter sidebar
    list_filter = ('is_active', 'user')

    # Adds a search bar
    search_fields = ('name', 'target_url')