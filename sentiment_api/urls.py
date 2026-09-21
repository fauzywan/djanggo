from django.urls import path
from .views import (
    AnalyzeSentimentView,
    DownloadResultView,
    HealthCheckView,
    DownloadPDFView,
    SingleReviewPredictView,
    HistoryListView,
)

app_name = 'sentiment_api'

urlpatterns = [
    # Analisis dataset CSV
    path('analyze', AnalyzeSentimentView.as_view(), name='analyze_sentiment'),
    path('analyze/', AnalyzeSentimentView.as_view()),

    # Unduh hasil analisis berupa berkas CSV
    path('download-csv', DownloadResultView.as_view(), name='download_csv'),
    path('download-csv/', DownloadResultView.as_view()),

    # Health check server & model status
    path('health', HealthCheckView.as_view(), name='health_check'),
    path('health/', HealthCheckView.as_view()),

    # Pengujian pada satu ulasan
    path('predict-single', SingleReviewPredictView.as_view(), name='predict_single'),
    path('predict-single/', SingleReviewPredictView.as_view()),

    # Unduh PDF
    path('download-pdf', DownloadPDFView.as_view(), name='download_pdf'),
    path('download-pdf/', DownloadPDFView.as_view()),

    # Riwayat analisis
    path('history', HistoryListView.as_view(), name='history'),
    path('history/', HistoryListView.as_view()),
]
