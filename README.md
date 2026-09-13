# Backend Analisis Sentimen Ulasan Na Willa (Django + React)

Backend REST API untuk sistem analisis sentimen ulasan film Na Willa yang dibangun menggunakan **Django REST Framework (DRF)** dengan penerapan prinsip **Object-Oriented Programming (OOP)** secara ketat dan arsitektur decoupled (Headless) untuk frontend **React JS**.

---

## 🏛️ Arsitektur OOP & Struktur Proyek

```
djanggo/
├── manage.py                          # Django management CLI
├── requirements.txt                   # Dependensi backend
├── ml_models/                         # Direktori penyimpanan berkas model AI (.pkl)
│   └── README.md                      # Panduan peletakan model.pkl & vectorizer.pkl
├── nawilla_backend/                   # Konfigurasi Proyek Django
│   ├── settings.py                    # Konfigurasi DRF, CORS Headers, Paths
│   ├── urls.py                        # Root URL routing (/api/v1/)
│   ├── wsgi.py
│   └── asgi.py
├── sentiment_api/                     # Aplikasi Utama Analisis Sentimen
│   ├── apps.py                        # App Configuration
│   ├── models.py                      # Model log/history analisis ulasan
│   ├── serializers.py                 # OOP Serializer (validasi CSV UTF-8 & review_text)
│   ├── services.py                    # Core OOP Service Layer (ABC, SVM, Text Preprocessing)
│   ├── views.py                       # Class-Based Views (CBV APIView)
│   ├── urls.py                        # Endpoint mapping API v1
│   └── tests.py                       # Unit test menyeluruh
└── react_integration/
    └── api.js                         # Modul klien Axios siap pakai untuk React
```

---

## 🧩 Penerapan Prinsip OOP

1. **Abstraction (`BaseSentimentPredictor` di [services.py](file:///d:/djanggo/djanggo/sentiment_api/services.py))**:
   - Menggunakan `abc.ABC` dan `@abstractmethod` untuk mendefinisikan interface umum model AI (`load_model`, `predict`, `model_name`).
2. **Encapsulation**:
   - `TextPreprocessor`: Membungkus logika pembersihan teks ulasan dan ekstraksi kata kunci.
   - `SVMModelService`: Membungkus siklus hidup model `.pkl` menggunakan pola *Singleton/Cached instance*. Jika berkas `.pkl` belum tersedia, otomatis beralih ke *fallback leksikon* tanpa membuat aplikasi crash.
   - `WordFrequencyService`: Menghitung frekuensi kata bermakna untuk visualisasi Word Cloud.
   - `SentimentAnalysisService`: Mengorkestrasi pemrosesan dataset CSV, penghitungan distribusi, dan pembuatan respons data.
3. **Class-Based Views (CBV)**:
   - Semua endpoint dibungkus dalam class turunan `APIView` (`AnalyzeSentimentView`, `DownloadResultView`, `HealthCheckView`, `SingleReviewPredictView`).
4. **Data Contract & Serializer**:
   - `CSVUploadSerializer`: Memvalidasi encoding UTF-8, tipe berkas `.csv`, dan keberadaan kolom wajib `review_text`, sekaligus mempertahankan kolom tambahan (`reviewer`, `rating`, `date`, `review_url`).

---

## 🚀 Cara Menjalankan Backend

### Opsi 1: Menggunakan Berkas Batch (Paling Mudah - 1 Klik)
Cukup **klik ganda (double-click)** pada file:
- **`run.bat`** : Otomatis membuat `venv` jika belum ada, menginstal dependensi dari `requirements.txt`, menjalankan migrasi awal, dan langsung menyalakan server di `http://127.0.0.1:8000/`.
- **`test.bat`** : Menjalankan test suite unit test secara otomatis.
- **`install.bat`** : Khusus untuk menginstal atau memperbarui dependensi `requirements.txt`.

### Opsi 2: Manual via Terminal (PowerShell / CMD)
```bash
# 1. Buat & aktifkan virtual environment
python -m venv venv
.\venv\Scripts\activate

# 2. Install dependensi & migrasi
pip install -r requirements.txt
python manage.py migrate

# 3. Jalankan server
python manage.py runserver 8000
```
Server akan aktif di: `http://localhost:8000/`


---

## 📡 Daftar Endpoint API (v1)

| Method | Endpoint | Deskripsi |
|---|---|---|
| `POST` | `/api/v1/analyze` | Mengunggah fail CSV (`multipart/form-data`) dengan kolom `review_text` untuk dianalisis |
| `GET` | `/api/v1/download-csv` | Mengunduh fail CSV dari hasil analisis sentimen terakhir |
| `GET` | `/api/v1/health` | Memeriksa kesehatan server dan status model machine learning |
| `POST` | `/api/v1/predict-single` | Menguji inferensi sentimen pada satu kalimat ulasan ulasan |

---

## 📊 Contoh Respons JSON (`POST /api/v1/analyze`)

```json
{
  "status": "success",
  "metadata": {
    "file_name": "test_na_willa.csv",
    "total_rows_uploaded": 2622,
    "valid_rows_processed": 2622,
    "model_used": "Support Vector Machine",
    "processing_time_seconds": 1.5
  },
  "distribution": {
    "positif": { "count": 1746, "percentage": 66.59 },
    "netral": { "count": 450, "percentage": 17.16 },
    "negatif": { "count": 426, "percentage": 16.25 }
  },
  "results": [
    {
      "id": 1,
      "original_text": "filmnya lucu banget",
      "processed_text": "film lucu banget",
      "predicted_sentiment": "Positif"
    },
    {
      "id": 2,
      "original_text": "ceritanya biasa saja",
      "processed_text": "cerita biasa saja",
      "predicted_sentiment": "Netral"
    }
  ],
  "word_frequencies": [
    { "text": "lucu", "value": 150 },
    { "text": "bagus", "value": 120 }
  ]
}
```

---

## ⚛️ Integrasi dengan React JS

File konfigurasi dan pemanggilan Axios sudah disediakan di:
`react_integration/api.js`

Contoh pemanggilan di komponen React (`UploadPage.jsx`):
```javascript
import React, { useState } from 'react';
import { api } from './api';

function UploadPage() {
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleUpload = async () => {
    if (!file) return;
    setLoading(true);
    try {
      const data = await api.analyzeCSV(file);
      console.log("Hasil analisis:", data);
      // Simpan data ke state / context untuk Dashboard, Visualisasi, dan Ulasan
    } catch (err) {
      console.error("Gagal menganalisis CSV:", err.response?.data || err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <input type="file" accept=".csv" onChange={(e) => setFile(e.target.files[0])} />
      <button onClick={handleUpload} disabled={loading}>
        {loading ? 'Memproses...' : 'Analisis Sentimen'}
      </button>
    </div>
  );
}
```

---

## 🧪 Menjalankan Unit Test
Untuk memverifikasi fungsionalitas OOP dan endpoint API:
```bash
python manage.py test sentiment_api
```