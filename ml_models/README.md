# Direktori Model Machine Learning (.pkl)

Simpan berkas model AI Anda di folder ini:
1. `model.pkl` : Model klasifikasi sentimen ulasan (misal Support Vector Machine / Pipeline)
2. `vectorizer.pkl` (opsional jika vectorizer terpisah dari model)

Catatan:
Jika berkas `model.pkl` belum diletakkan di sini, backend Django akan secara otomatis mengaktifkan 'Fallback Predictor' berbasis leksikon ulasan film sehingga server tetap dapat berjalan dan frontend React dapat diuji tanpa hambatan.
