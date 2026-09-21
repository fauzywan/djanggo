from django.db import models


class Dataset(models.Model):
    """
    Tabel 'dataset' (Sesuai Sub-bab 4.4.3 Tabel 4.x Skripsi)
    Menyimpan identitas berkas CSV dan ringkasan distribusi sentimen.
    """
    nama_file = models.CharField(max_length=255)
    tanggal_upload = models.DateTimeField(auto_now_add=True)
    jumlah_data = models.IntegerField(default=0)
    jumlah_positif = models.IntegerField(default=0)
    jumlah_netral = models.IntegerField(default=0)
    jumlah_negatif = models.IntegerField(default=0)
    processing_time_seconds = models.FloatField(default=0.0)

    class Meta:
        db_table = 'dataset'
        ordering = ['-tanggal_upload']
        verbose_name = 'Dataset'
        verbose_name_plural = 'Daftar Dataset'

    def __str__(self):
        return f"{self.nama_file} ({self.tanggal_upload.strftime('%Y-%m-%d %H:%M')})"


class ModelML(models.Model):
    """
    Tabel 'model' (Sesuai Sub-bab 4.4.3 Tabel 4.x Skripsi)
    Menyimpan informasi model klasifikasi dan metrik performa evaluasi.
    """
    nama_model = models.CharField(max_length=100, default="Support Vector Machine")
    accuracy = models.FloatField(default=0.0)
    precision = models.FloatField(default=0.0)
    recall = models.FloatField(default=0.0)
    f1_score = models.FloatField(default=0.0)

    class Meta:
        db_table = 'model'
        verbose_name = 'Model ML'
        verbose_name_plural = 'Daftar Model ML'

    def __str__(self):
        return f"{self.nama_model} (F1: {self.f1_score:.4f})"


class Ulasan(models.Model):
    """
    Tabel 'ulasan' (Sesuai Sub-bab 4.4.3 Tabel 4.x Skripsi)
    Menyimpan data setiap baris ulasan dan hasil prediksinya.
    """
    dataset = models.ForeignKey(Dataset, on_delete=models.CASCADE, related_name='ulasan_list')
    tanggal = models.DateField(null=True, blank=True)
    review_text = models.TextField()
    label_sentimen = models.CharField(max_length=20, null=True, blank=True)
    hasil_prediksi = models.CharField(max_length=20)

    class Meta:
        db_table = 'ulasan'
        verbose_name = 'Ulasan'
        verbose_name_plural = 'Daftar Ulasan'

    def __str__(self):
        return f"Ulasan {self.id}: {self.hasil_prediksi}"


class AnalysisHistory(models.Model):
    """
    Model log untuk menyimpan riwayat analisis dataset CSV (kompatibilitas).
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
