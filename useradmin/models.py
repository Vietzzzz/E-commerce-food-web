from django.db import models


class DashboardAnalytics(models.Model):
    date_created = models.DateTimeField(auto_now_add=True)
    data_type = models.CharField(max_length=100)
    label = models.CharField(max_length=255)
    count = models.IntegerField(null=True, blank=True)
    value = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    class Meta:
        verbose_name_plural = "Dashboard Analytics"
        ordering = ["-date_created"]

    def __str__(self):
        return f"{self.data_type} - {self.date_created.strftime('%Y-%m-%d')}"
