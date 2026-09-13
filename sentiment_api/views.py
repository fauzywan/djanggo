"""
Class-Based Views (CBV) untuk API Analisis Sentimen Na Willa.
Mengikuti arsitektur OOP dengan memisahkan Controller (View) dari Business Logic (Service).
"""

import io
import pandas as pd
from django.http import HttpResponse
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser

from .serializers import CSVUploadSerializer, SingleReviewSerializer
from .services import SentimentAnalysisService, SVMModelService


class AnalyzeSentimentView(APIView):
    """
    Class-Based View: POST /api/v1/analyze
    Menerima berkas CSV melalui multipart/form-data, memvalidasi masukan,
    melakukan prapemrosesan teks, inferensi model SVM, dan mengembalikan
    respons JSON terstruktur presisi untuk konsumsi frontend React.
    """
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request, *args, **kwargs):
        serializer = CSVUploadSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(
                {
                    "status": "error",
                    "message": "Validasi berkas CSV gagal.",
                    "errors": serializer.errors
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            file_obj = serializer.validated_data['file']
            df = serializer.get_dataframe()

            # Delegasikan seluruh logika pemrosesan ke Service Layer (OOP)
            analysis_service = SentimentAnalysisService()
            response_payload = analysis_service.analyze_dataframe(df=df, file_name=file_obj.name)

            return Response(response_payload, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {
                    "status": "error",
                    "message": f"Terjadi kesalahan saat memproses berkas CSV: {str(e)}"
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class DownloadResultView(APIView):
    """
    Class-Based View: GET /api/v1/download-csv
    Menghasilkan berkas CSV dari data hasil analisis sentimen terakhir.
    """

    def get(self, request, *args, **kwargs):
        last_df, file_name = SentimentAnalysisService.get_last_analyzed_dataframe()

        if last_df is None or last_df.empty:
            return Response(
                {
                    "status": "error",
                    "message": "Belum ada dataset yang dianalisis. Silakan unggah CSV terlebih dahulu."
                },
                status=status.HTTP_404_NOT_FOUND
            )

        output = io.StringIO()
        last_df.to_csv(output, index=False, encoding='utf-8')
        output.seek(0)

        response = HttpResponse(output.getvalue(), content_type='text/csv; charset=utf-8')
        export_name = f"hasil_analisis_{file_name}" if not file_name.startswith("hasil_") else file_name
        response['Content-Disposition'] = f'attachment; filename="{export_name}"'
        return response


class HealthCheckView(APIView):
    """
    Class-Based View: GET /api/v1/health
    Memastikan server Django dan model klasifikasi AI telah aktif.
    """

    def get(self, request, *args, **kwargs):
        svm_service = SVMModelService()
        return Response(
            {
                "status": "healthy",
                "service": "Na Willa Sentiment Analysis Backend",
                "model_info": {
                    "name": svm_service.model_name,
                    "is_loaded": svm_service.is_loaded,
                    "model_path": str(svm_service.model_path),
                    "mode": "production_pkl" if svm_service.is_loaded else "development_fallback"
                }
            },
            status=status.HTTP_200_OK
        )


class SingleReviewPredictView(APIView):
    """
    Class-Based View: POST /api/v1/predict-single
    Melakukan pengujian analisis sentimen langsung pada satu buah teks ulasan.
    """
    parser_classes = [JSONParser, FormParser, MultiPartParser]

    def post(self, request, *args, **kwargs):
        serializer = SingleReviewSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(
                {
                    "status": "error",
                    "message": "Input teks tidak valid.",
                    "errors": serializer.errors
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        text = serializer.validated_data['text']
        analysis_service = SentimentAnalysisService()
        result_payload = analysis_service.analyze_single_review(text=text)

        return Response(result_payload, status=status.HTTP_200_OK)
