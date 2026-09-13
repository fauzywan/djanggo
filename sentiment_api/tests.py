import io
import pandas as pd
from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APIClient
from rest_framework import status

from .services import TextPreprocessor, SVMModelService, SentimentAnalysisService, WordFrequencyService
from .serializers import CSVUploadSerializer, SingleReviewSerializer


class TextPreprocessorTests(TestCase):
    def setUp(self):
        self.preprocessor = TextPreprocessor()

    def test_clean_text(self):
        raw = "Filmnya Lucu BANGET!!! https://example.com recommended 100%"
        cleaned = self.preprocessor.clean(raw)
        self.assertEqual(cleaned, "filmnya lucu banget recommended")

    def test_extract_keywords(self):
        text = "film yang sangat lucu dan bagus sekali"
        keywords = self.preprocessor.extract_keywords(text)
        self.assertIn("lucu", keywords)
        self.assertIn("bagus", keywords)
        # 'yang' and 'dan' should be removed by stopwords
        self.assertNotIn("yang", keywords)
        self.assertNotIn("dan", keywords)


class SentimentServicesTests(TestCase):
    def setUp(self):
        self.service = SentimentAnalysisService()

    def test_single_review_prediction(self):
        res = self.service.analyze_single_review("filmnya lucu dan sangat menghibur")
        self.assertEqual(res["status"], "success")
        self.assertEqual(res["result"]["predicted_sentiment"], "Positif")

    def test_dataframe_analysis_output_contract(self):
        # Buat dataframe ulasan tiruan
        data = {
            "reviewer": ["User1", "User2", "User3"],
            "rating": [5, 3, 1],
            "review_text": [
                "filmnya lucu banget dan bagus",
                "ceritanya biasa saja dan standar",
                "jelek banget membosankan dan kecewa"
            ],
            "date": ["2024-01-01", "2024-01-02", "2024-01-03"]
        }
        df = pd.DataFrame(data)
        response_data = self.service.analyze_dataframe(df, file_name="sample_test.csv")

        # Verifikasi format kontrak respons persis sesuai blueprint
        self.assertEqual(response_data["status"], "success")
        self.assertIn("metadata", response_data)
        self.assertIn("distribution", response_data)
        self.assertIn("results", response_data)
        self.assertIn("word_frequencies", response_data)

        self.assertEqual(response_data["metadata"]["file_name"], "sample_test.csv")
        self.assertEqual(response_data["metadata"]["total_rows_uploaded"], 3)
        self.assertEqual(response_data["metadata"]["valid_rows_processed"], 3)

        # Cek distribusi sentimen
        dist = response_data["distribution"]
        self.assertIn("positif", dist)
        self.assertIn("netral", dist)
        self.assertIn("negatif", dist)
        self.assertEqual(dist["positif"]["count"] + dist["netral"]["count"] + dist["negatif"]["count"], 3)

        # Cek results array
        results = response_data["results"]
        self.assertEqual(len(results), 3)
        self.assertEqual(results[0]["id"], 1)
        self.assertIn("original_text", results[0])
        self.assertIn("processed_text", results[0])
        self.assertIn("predicted_sentiment", results[0])


class SentimentAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_health_check_endpoint(self):
        response = self.client.get('/api/v1/health')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], "healthy")

    def test_predict_single_endpoint(self):
        response = self.client.post('/api/v1/predict-single', {'text': 'Filmnya lucu banget'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], "success")
        self.assertEqual(response.data["result"]["predicted_sentiment"], "Positif")

    def test_analyze_csv_valid(self):
        csv_content = (
            "reviewer,rating,review_text,date\n"
            "Budi,5,filmnya lucu banget,2024-01-01\n"
            "Ani,3,ceritanya biasa saja,2024-01-02\n"
        ).encode('utf-8')

        uploaded_file = SimpleUploadedFile("test_ulasan.csv", csv_content, content_type="text/csv")
        response = self.client.post('/api/v1/analyze', {'file': uploaded_file}, format='multipart')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], "success")
        self.assertEqual(response.data["metadata"]["valid_rows_processed"], 2)

    def test_analyze_csv_invalid_missing_review_text_column(self):
        csv_content = (
            "reviewer,rating,komentar\n"
            "Budi,5,filmnya bagus\n"
        ).encode('utf-8')

        uploaded_file = SimpleUploadedFile("invalid.csv", csv_content, content_type="text/csv")
        response = self.client.post('/api/v1/analyze', {'file': uploaded_file}, format='multipart')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["status"], "error")

    def test_download_csv_endpoint(self):
        # 1. Upload CSV terlebih dahulu
        csv_content = "review_text\nfilm bagus\n".encode('utf-8')
        uploaded_file = SimpleUploadedFile("test.csv", csv_content, content_type="text/csv")
        self.client.post('/api/v1/analyze', {'file': uploaded_file}, format='multipart')

        # 2. Download hasil
        response = self.client.get('/api/v1/download-csv')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'text/csv; charset=utf-8')

    def test_test_page_loads(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

