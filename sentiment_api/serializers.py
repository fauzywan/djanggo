import io
import pandas as pd
from rest_framework import serializers
from .models import AnalysisHistory

class AnalysisHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = AnalysisHistory
        fields = '__all__'

class CSVUploadSerializer(serializers.Serializer):
    """
    Serializer OOP untuk memvalidasi berkas CSV yang diunggah.
    Kontrak:
    - Ekstensi wajib .csv
    - Encoding wajib UTF-8
    - Wajib memiliki kolom 'review_text'
    - Kolom opsional (reviewer, rating, date, review_url, dll) dipertahankan
    """
    file = serializers.FileField(required=True)

    REQUIRED_COLUMN = 'review_text'
    MAX_FILE_SIZE_MB = 50

    def validate_file(self, file_obj):
        # 1. Validasi Ekstensi
        if not file_obj.name.lower().endswith('.csv'):
            raise serializers.ValidationError("Berkas yang diunggah harus memiliki format CSV (.csv).")

        # 2. Validasi Ukuran Berkas
        if file_obj.size > self.MAX_FILE_SIZE_MB * 1024 * 1024:
            raise serializers.ValidationError(f"Ukuran berkas tidak boleh melebihi {self.MAX_FILE_SIZE_MB} MB.")

        # 3. Validasi Encoding UTF-8 dan Keterbacaan CSV
        try:
            # Baca byte awal untuk memastikan UTF-8
            file_obj.seek(0)
            raw_bytes = file_obj.read(4096)
            raw_bytes.decode('utf-8')
        except UnicodeDecodeError:
            raise serializers.ValidationError("Berkas CSV wajib ber-encoding UTF-8.")

        # 4. Validasi Keberadaan Kolom review_text menggunakan pandas
        try:
            file_obj.seek(0)
            sample_df = pd.read_csv(file_obj, nrows=5, encoding='utf-8')
            file_obj.seek(0)  # reset pointer kembali ke awal
        except Exception as err:
            raise serializers.ValidationError(f"Gagal membaca format CSV: {str(err)}")

        # Normalisasi nama kolom (strip whitespace)
        columns = [col.strip() for col in sample_df.columns]
        if self.REQUIRED_COLUMN not in columns:
            raise serializers.ValidationError(
                f"Berkas CSV wajib memuat kolom target bernama '{self.REQUIRED_COLUMN}'. "
                f"Kolom yang ditemukan: {', '.join(columns)}"
            )

        return file_obj

    def get_dataframe(self) -> pd.DataFrame:
        """
        Mengonversi fail CSV yang telah divalidasi ke pandas DataFrame
        dengan encoding UTF-8 dan mempertahankan semua kolom tambahan.
        """
        file_obj = self.validated_data['file']
        file_obj.seek(0)
        df = pd.read_csv(file_obj, encoding='utf-8')
        # Bersihkan nama kolom dari whitespace
        df.columns = [col.strip() for col in df.columns]
        return df


class SingleReviewSerializer(serializers.Serializer):
    """
    Serializer OOP untuk pengujian inferensi pada ulasan tunggal.
    """
    text = serializers.CharField(
        required=True,
        min_length=1,
        max_length=5000,
        error_messages={
            'required': 'Kolom ulasan (text) wajib diisi.',
            'blank': 'Ulasan tidak boleh kosong.'
        }
    )
