"""
Service Layer untuk Analisis Sentimen Film Na Willa.
Menerapkan Prinsip Object-Oriented Programming (OOP) secara ketat:
- Abstraction: BaseSentimentPredictor (Abstract Base Class)
- Encapsulation: TextPreprocessor, SVMModelService, WordFrequencyService, SentimentAnalysisService
- Polymorphism: Kemampuan berganti model (SVM / CNN / Fallback)

Menggunakan konfigurasi artefak final:
- ml_models/metadata_model_final.json
- ml_models/slang_dict_final.json
- ml_models/stopwords_svm_final.json
- ml_models/svm_na_willa_final.pkl
- ml_models/tfidf_na_willa_final.pkl
"""

from abc import ABC, abstractmethod
from collections import Counter
from pathlib import Path
import json
import re
import string
import time
import logging
import joblib
import pandas as pd
import warnings
from .models import AnalysisHistory


try:
    from sklearn.exceptions import InconsistentVersionWarning
    warnings.filterwarnings("ignore", category=InconsistentVersionWarning)
except ImportError:
    pass

from django.conf import settings

logger = logging.getLogger(__name__)



# =====================================================================
# 1. ABSTRACTION: Base Interface untuk Predictor Model AI
# =====================================================================
class BaseSentimentPredictor(ABC):
    """
    Abstract Base Class yang mendefinisikan kontrak method wajib
    untuk model klasifikasi sentimen ulasan.
    """

    @abstractmethod
    def load_model(self) -> bool:
        """Memuat model dan vectorizer dari berkas serialisasi (.pkl)."""
        pass

    @abstractmethod
    def predict(self, texts: list[str]) -> list[str]:
        """
        Menerima sekumpulan teks hasil prapemrosesan dan
        mengembalikan list label prediksi sentimen baku ('Positif', 'Netral', 'Negatif').
        """
        pass

    @property
    @abstractmethod
    def model_name(self) -> str:
        """Nama representasi model yang digunakan."""
        pass


# =====================================================================
# 2. ENCAPSULATION: Prapemrosesan Teks (Text Preprocessor)
#   Sesuai pipeline metadata: cleaning, case_folding, tokenisasi, normalisasi,
#   stopword_removal_selektif, stemming.
# =====================================================================
class TextPreprocessor:
    """
    Kelas prapemrosesan teks komprehensif untuk ulasan film Na Willa.
    Memanfaatkan slang_dict_final.json dan stopwords_svm_final.json.
    """

    def __init__(
        self,
        slang_path: Path | str | None = None,
        stopwords_path: Path | str | None = None
    ):
        self.slang_path = Path(slang_path or getattr(settings, 'SLANG_DICT_PATH', 'ml_models/slang_dict_final.json'))
        self.stopwords_path = Path(stopwords_path or getattr(settings, 'STOPWORDS_SVM_PATH', 'ml_models/stopwords_svm_final.json'))
        
        self.slang_dict = self._load_slang_dict()
        self.stopwords = self._load_stopwords()
        self._stemmer = self._init_stemmer()

    def _load_slang_dict(self) -> dict[str, str]:
        """Memuat kamus normalisasi kata gaul/singkatan dari JSON."""
        if self.slang_path.exists():
            try:
                with open(self.slang_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Gagal membaca slang dict: {e}")
        return {}

    def _load_stopwords(self) -> set[str]:
        """Memuat daftar stopword selektif SVM dari JSON."""
        if self.stopwords_path.exists():
            try:
                with open(self.stopwords_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return set(data) if isinstance(data, list) else set(data.keys())
            except Exception as e:
                logger.warning(f"Gagal membaca stopwords: {e}")
        return {
            'yang', 'untuk', 'pada', 'ke', 'para', 'dan', 'ini', 'karena', 'oleh',
            'saat', 'harus', 'bisa', 'dari', 'itu', 'di', 'ada', 'akan', 'atau'
        }

    def _init_stemmer(self):
        """Inisialisasi stemmer bahasa Indonesia (Sastrawi) jika terpasang."""
        try:
            from Sastrawi.Stemmer.StemmerFactory import StemmerFactory
            factory = StemmerFactory()
            return factory.create_stemmer()
        except ImportError:
            # Jika pustaka Sastrawi belum dipasang, fallback pasif
            return None

    def clean(self, text: str) -> str:
        """
        Tahap 1: Cleaning & Case Folding
        - Lowercase
        - Hapus URL, mention, hashtag
        - Hapus tanda baca dan angka
        - Hapus spasi berlebih
        """
        if not isinstance(text, str):
            text = str(text) if text is not None else ""

        cleaned = text.lower().strip()
        cleaned = re.sub(r'https?://\S+|www\.\S+', ' ', cleaned)
        cleaned = cleaned.translate(str.maketrans('', '', string.punctuation))
        cleaned = re.sub(r'\d+', ' ', cleaned)
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()
        return cleaned

    def normalize_slang(self, text: str) -> str:
        """
        Tahap 2: Normalisasi Slang & Singkatan (tokenisasi & penggantian kata)
        """
        words = text.split()
        normalized_words = [self.slang_dict.get(w, w) for w in words]
        return " ".join(normalized_words)

    def remove_stopwords(self, text: str) -> str:
        """
        Tahap 3: Penghapusan Stopwords Selektif untuk SVM
        """
        words = text.split()
        filtered_words = [w for w in words if w not in self.stopwords]
        return " ".join(filtered_words)

    def stem(self, text: str) -> str:
        """
        Tahap 4: Stemming kata dasar bahasa Indonesia
        """
        if self._stemmer:
            try:
                return self._stemmer.stem(text)
            except Exception:
                return text
        return text

    def preprocess_for_svm(self, text: str) -> str:
        """
        Alur lengkap prapemrosesan teks sesuai spesifikasi pipeline SVM:
        cleaning -> case_folding -> tokenisasi -> normalisasi -> stopword_removal_selektif -> stemming
        """
        t = self.clean(text)
        t = self.normalize_slang(t)
        t = self.remove_stopwords(t)
        t = self.stem(t)
        return t

    def extract_keywords(self, text: str) -> list[str]:
        """Ekstraksi kata bermakna untuk analisis frekuensi kata / word cloud."""
        cleaned = self.clean(text)
        normalized = self.normalize_slang(cleaned)
        words = normalized.split()
        return [w for w in words if len(w) > 2 and w not in self.stopwords]


# =====================================================================
# 3. CONCRETE IMPLEMENTATION: SVM Model Service (LinearSVC)
# =====================================================================
class SVMModelService(BaseSentimentPredictor):
    """
    Layanan inferensi menggunakan model Support Vector Machine (LinearSVC)
    dan TF-IDF Vectorizer. Menerapkan pola Singleton/Cached Instance.
    """

    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(SVMModelService, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(
        self,
        model_path: Path | str | None = None,
        vectorizer_path: Path | str | None = None,
        metadata_path: Path | str | None = None
    ):
        if self._initialized:
            return

        self.model_path = Path(model_path or getattr(settings, 'SVM_MODEL_PATH', 'ml_models/svm_na_willa_final.pkl'))
        self.vectorizer_path = Path(vectorizer_path or getattr(settings, 'TFIDF_VECTORIZER_PATH', 'ml_models/tfidf_na_willa_final.pkl'))
        self.metadata_path = Path(metadata_path or getattr(settings, 'METADATA_MODEL_PATH', 'ml_models/metadata_model_final.json'))

        self.model = None
        self.vectorizer = None
        self.metadata = {}
        self._is_loaded = False

        self.load_metadata()
        self.load_model()
        self._initialized = True

    @property
    def model_name(self) -> str:
        return "Support Vector Machine"

    @property
    def is_loaded(self) -> bool:
        return self._is_loaded

    def load_metadata(self):
        """Membaca file metadata_model_final.json jika ada."""
        if self.metadata_path.exists():
            try:
                with open(self.metadata_path, 'r', encoding='utf-8') as f:
                    self.metadata = json.load(f)
                    logger.info("Berhasil membaca metadata_model_final.json")
            except Exception as e:
                logger.warning(f"Gagal membaca metadata: {e}")

    def load_model(self) -> bool:
        """
        Memuat model svm_na_willa_final.pkl dan tfidf_na_willa_final.pkl.
        """
        try:
            model_exists = self.model_path.exists()
            vectorizer_exists = self.vectorizer_path.exists()

            if model_exists and vectorizer_exists:
                logger.info(f"Memuat model SVM dari: {self.model_path}")
                self.model = joblib.load(self.model_path)
                logger.info(f"Memuat vectorizer TF-IDF dari: {self.vectorizer_path}")
                self.vectorizer = joblib.load(self.vectorizer_path)
                self._is_loaded = True
                return True
            else:
                missing = []
                if not model_exists:
                    missing.append(str(self.model_path))
                if not vectorizer_exists:
                    missing.append(str(self.vectorizer_path))
                logger.warning(
                    f"Berkas model/vectorizer belum ditemukan ({', '.join(missing)}). "
                    "Mengaktifkan Fallback Predictor berbasis leksikon untuk pengembangan."
                )
                self._is_loaded = False
                return False
        except Exception as e:
            logger.error(f"Gagal memuat berkas .pkl: {e}")
            self._is_loaded = False
            return False

    def predict(self, texts: list[str]) -> list[str]:
        """
        Inferensi klasifikasi sentimen:
        1. Vektorisasi teks menggunakan TF-IDF
        2. Klasifikasi menggunakan LinearSVC
        3. Normalisasi label ke 'Positif', 'Netral', 'Negatif'
        """
        if not texts:
            return []

        if self._is_loaded and self.model is not None and self.vectorizer is not None:
            try:
                X_tfidf = self.vectorizer.transform(texts)
                raw_preds = self.model.predict(X_tfidf)
                return [self._map_label(p) for p in raw_preds]
            except Exception as e:
                logger.error(f"Error saat inferensi SVM: {e}. Beralih ke fallback.")

        # Fallback leksikon ulasan film
        return [self._fallback_predict_single(t) for t in texts]

    def _map_label(self, raw_label) -> str:
        """
        Memetakan label output model ke format standar: Positif, Netral, Negatif.
        Mendukung pemetaan numerik (0=negatif, 1=netral, 2=positif) maupun string.
        """
        label_str = str(raw_label).strip().lower()
        if label_str in ['2', 'positif', 'positive', 'pos']:
            return "Positif"
        elif label_str in ['0', 'negatif', 'negative', 'neg', '-1']:
            return "Negatif"
        elif label_str in ['1', 'netral', 'neutral', 'neu']:
            return "Netral"
        return str(raw_label).capitalize()

    def _fallback_predict_single(self, text: str) -> str:
        """Prediktor cadangan berbasis kata kunci sentimen."""
        lower = text.lower()
        positive_cues = ['lucu', 'bagus', 'keren', 'suka', 'indah', 'hebat', 'menghibur', 'hangat', 'gemas', 'senang', 'terbaik', 'puas']
        negative_cues = ['jelek', 'bosan', 'kecewa', 'buruk', 'gagal', 'kurang', 'membosankan', 'rusak', 'kesal', 'rugi']

        pos_score = sum(1 for cue in positive_cues if cue in lower)
        neg_score = sum(1 for cue in negative_cues if cue in lower)

        if pos_score > neg_score:
            return "Positif"
        elif neg_score > pos_score:
            return "Negatif"
        return "Netral"


# =====================================================================
# 4. ENCAPSULATION: Analisis Frekuensi Kata (Word Frequency)
# =====================================================================
class WordFrequencyService:
    """Kelas untuk menghitung frekuensi kata untuk visualisasi Word Cloud."""

    @staticmethod
    def calculate(texts: list[str], top_n: int = 50, preprocessor: TextPreprocessor | None = None) -> list[dict]:
        prep = preprocessor or TextPreprocessor()
        counter = Counter()

        for text in texts:
            words = prep.extract_keywords(text)
            counter.update(words)

        return [{"text": word, "value": count} for word, count in counter.most_common(top_n)]


# =====================================================================
# 5. ORCHESTRATOR: Sentiment Analysis Service (Utama)
# =====================================================================
class SentimentAnalysisService:
    """
    Kelas Orchestrator yang mengoordinasikan seluruh alur kerja:
    1. Validasi baris dataframe
    2. Prapemrosesan teks (clean -> normalize slang -> stopword removal -> stemming)
    3. Inferensi model SVM
    4. Perhitungan statistik distribusi
    5. Perhitungan frekuensi kata
    6. Pembuatan respons JSON sesuai kontrak presisi
    """

    _last_analyzed_dataframe: pd.DataFrame | None = None
    _last_file_name: str = "sentiment_results.csv"

    def __init__(self, predictor: BaseSentimentPredictor | None = None, preprocessor: TextPreprocessor | None = None):
        self.predictor = predictor or SVMModelService()
        self.preprocessor = preprocessor or TextPreprocessor()

    def analyze_dataframe(self, df: pd.DataFrame, file_name: str = "dataset.csv") -> dict:
        start_time = time.time()
        total_rows_uploaded = len(df)

        # 1. Filter baris ulasan yang valid
        valid_df = df.dropna(subset=['review_text']).copy()
        valid_df['review_text'] = valid_df['review_text'].astype(str)
        valid_df = valid_df[valid_df['review_text'].str.strip() != ''].copy()
        valid_rows_processed = len(valid_df)

        # 2. Prapemrosesan teks ulasan (pipeline lengkap)
        original_texts = valid_df['review_text'].tolist()
        processed_texts = [self.preprocessor.preprocess_for_svm(t) for t in original_texts]
        valid_df['processed_text'] = processed_texts

        # 3. Prediksi Sentimen menggunakan Model SVM
        predicted_sentiments = self.predictor.predict(processed_texts)
        valid_df['predicted_sentiment'] = predicted_sentiments

        # Simpan state untuk endpoint unduh CSV
        SentimentAnalysisService._last_analyzed_dataframe = valid_df.copy()
        SentimentAnalysisService._last_file_name = file_name

        # 4. Hitung Distribusi Sentimen
        pos_count = sum(1 for s in predicted_sentiments if s == "Positif")
        net_count = sum(1 for s in predicted_sentiments if s == "Netral")
        neg_count = sum(1 for s in predicted_sentiments if s == "Negatif")

        def calc_percentage(count: int, total: int) -> float:
            return round((count / total * 100), 2) if total > 0 else 0.0

        distribution = {
            "positif": {
                "count": pos_count,
                "percentage": calc_percentage(pos_count, valid_rows_processed)
            },
            "netral": {
                "count": net_count,
                "percentage": calc_percentage(net_count, valid_rows_processed)
            },
            "negatif": {
                "count": neg_count,
                "percentage": calc_percentage(neg_count, valid_rows_processed)
            }
        }

        # 5. Format Hasil Ulasan Per Baris (Results)
        results = []
        for idx, (_, row) in enumerate(valid_df.iterrows(), start=1):
            item = {
                "id": idx,
                "original_text": row['review_text'],
                "processed_text": row['processed_text'],
                "predicted_sentiment": row['predicted_sentiment']
            }
            # Pertahankan kolom metadata tambahan jika ada
            for extra_col in ['reviewer', 'rating', 'date', 'review_url']:
                if extra_col in row and pd.notna(row[extra_col]):
                    item[extra_col] = row[extra_col]
            results.append(item)

        # 6. Hitung Frekuensi Kata untuk Visualisasi Word Cloud
        word_frequencies = WordFrequencyService.calculate(
            original_texts,
            top_n=50,
            preprocessor=self.preprocessor
        )

        # 7. Metadata Waktu & Berkas
        processing_time = round(time.time() - start_time, 3)

        # 8. Simpan riwayat secara permanen ke database menggunakan model AnalysisHistory
        AnalysisHistory.objects.create(
            file_name=file_name,
            total_rows=total_rows_uploaded,
            valid_rows=valid_rows_processed,
            model_used=self.predictor.model_name,
            positive_count=pos_count,
            neutral_count=net_count,
            negative_count=neg_count,
            processing_time_seconds=processing_time
        )

        return {
            "status": "success",
            "metadata": {
                "file_name": file_name,
                "total_rows_uploaded": total_rows_uploaded,
                "valid_rows_processed": valid_rows_processed,
                "model_used": self.predictor.model_name,
                "processing_time_seconds": processing_time
            },
            "distribution": distribution,
            "results": results,
            "word_frequencies": word_frequencies
        }

    def analyze_single_review(self, text: str) -> dict:
        start_time = time.time()
        processed = self.preprocessor.preprocess_for_svm(text)
        predictions = self.predictor.predict([processed])
        sentiment = predictions[0] if predictions else "Netral"

        return {
            "status": "success",
            "metadata": {
                "model_used": self.predictor.model_name,
                "processing_time_seconds": round(time.time() - start_time, 4)
            },
            "result": {
                "original_text": text,
                "processed_text": processed,
                "predicted_sentiment": sentiment
            }
        }

    @classmethod
    def get_last_analyzed_dataframe(cls) -> tuple[pd.DataFrame | None, str]:
        return cls._last_analyzed_dataframe, cls._last_file_name