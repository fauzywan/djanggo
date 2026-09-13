from django.urls import path
from .views import (
    AnalyzeSentimentView,
    DownloadResultView,
    HealthCheckView,
    SingleReviewPredictView,
)

app_name = 'sentiment_api'

urlpatterns = [
    # Analisis dataset CSV
    path('analyze', AnalyzeSentimentView.as_view(), name='analyze_sentiment'),

    # Unduh hasil analisis berupa berkas CSV
    path('download-csv', DownloadResultView.as_view(), name='download_csv'),

    # Health check server & model status
    path('health', HealthCheckView.as_view(), name='health_check'),

    # Pengujian pada satu ulasan
    path('predict-single', SingleReviewPredictView.as_view(), name='predict_single'),
]
