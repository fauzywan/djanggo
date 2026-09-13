from django.db import models


class AnalysisHistory(models.Model):
    """
    Model log untuk menyimpan riwayat analisis dataset CSV (opsional).
    Dapat digunakan jika ingin menyimpan rekap analisis ulasan ke database.
    """
    file_name = models.CharField(max_length=255)
    total_rows = models.IntegerField(default=0)
    valid_rows = models.IntegerField(default=0)
    model_used = models.CharField(max_length=100, default="Support Vector Machine")
    positive_count = models.IntegerField(default=0)
    neutral_count = models.IntegerField(default=0)
    negative_count = models.IntegerField(default=0)
    processing_time_seconds = models.FloatField(default=0.0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Analysis History'
        verbose_name_plural = 'Analysis Histories'

    def __str__(self):
        return f"{self.file_name} ({self.created_at.strftime('%Y-%m-%d %H:%M')})"
