from django.contrib import admin
from .models import Dataset, ModelML, Ulasan, AnalysisHistory

@admin.register(Dataset)
class DatasetAdmin(admin.ModelAdmin):
    list_display = ('nama_file', 'jumlah_data', 'jumlah_positif', 'jumlah_netral', 'jumlah_negatif', 'tanggal_upload')
    search_fields = ('nama_file',)
    list_filter = ('tanggal_upload',)

@admin.register(ModelML)
class ModelMLAdmin(admin.ModelAdmin):
    list_display = ('nama_model', 'accuracy', 'precision', 'recall', 'f1_score')
    search_fields = ('nama_model',)

@admin.register(Ulasan)
class UlasanAdmin(admin.ModelAdmin):
    list_display = ('id', 'dataset', 'hasil_prediksi', 'label_sentimen', 'tanggal')
    search_fields = ('review_text', 'hasil_prediksi')
    list_filter = ('hasil_prediksi', 'label_sentimen')

@admin.register(AnalysisHistory)
class AnalysisHistoryAdmin(admin.ModelAdmin):
    list_display = ('file_name', 'valid_rows', 'positive_count', 'neutral_count', 'negative_count', 'created_at')
    search_fields = ('file_name',)
