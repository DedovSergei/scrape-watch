# control_panel/jobs/models.py
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class ScrapeJob(models.Model):
    """
    Defines a single scrape job configuration.
    """
    # Core Config
    name = models.CharField(max_length=200, help_text="A human-readable name for this job (e.g., 'Bazos - BMW E30 Parts')")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="scrape_jobs")
    target_url = models.URLField(max_length=1024)
    is_active = models.BooleanField(default=True, help_text="Toggle this job on or off")

    # Scrape settings
    scrape_interval = models.DurationField(
        default=timezone.timedelta(hours=1),
        help_text="How often to run the scrape (e.g., '1 hour', '30 minutes')"
    )

    # CSS Selectors (the core of the scraper)
    css_selector_listing = models.CharField(max_length=500, help_text="CSS selector for the *container* of all listings")
    css_selector_title = models.CharField(max_length=500, help_text="CSS selector for the item title (relative to the listing container)")
    css_selector_price = models.CharField(max_length=500, help_text="CSS selector for the item price (relative to the listing container)")
    css_selector_url = models.CharField(max_length=500, help_text="CSS selector for the item's unique URL (relative to the listing container)")

    # Timestamps (good practice)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_scraped = models.DateTimeField(null=True, blank=True, editable=False)

    def __str__(self):
        return f"({self.user.username}) - {self.name}"

    class Meta:
        # Ensures one user can't have two jobs with the same name
        unique_together = ('user', 'name')