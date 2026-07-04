import os
import unittest
from fastapi.testclient import TestClient
from src.backend.main import app, metadata_db

class TestBackendIngestion(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        self.test_filename = "test_case_file.txt"
        metadata_db.clear()
        
        with open(self.test_filename, "w", encoding="utf-8") as f:
            f.write("Case details: Missing emerald necklace reported at 221B Baker St.")

    def tearDown(self):
        if os.path.exists(self.test_filename):
            os.remove(self.test_filename)

    def test_fr_2_1_successful_ingestion(self):
        """FR-2.1: Verify endpoint accepts file and form data, returning valid metadata."""
        with open(self.test_filename, "rb") as f:
            response = self.client.post(
                "/documents",
                data={"subject": "The Stolen Emerald"},
                files={"file": (self.test_filename, f, "text/plain")}
            )
            
        self.assertEqual(response.status_code, 201)
        data = response.json()
        self.assertIn("id", data)
        self.assertEqual(data["filename"], self.test_filename)
        self.assertEqual(data["subject"], "The Stolen Emerald")
        self.assertIn("date_added", data)

    def test_fr_2_1_reject_duplicate_files(self):
        """FR-2.1: Verify duplicate filenames trigger a 400 Bad Request error."""
        # First upload
        with open(self.test_filename, "rb") as f:
            self.client.post(
                "/documents",
                data={"subject": "Initial Case File"},
                files={"file": (self.test_filename, f, "text/plain")}
            )
            
        # Duplicate upload
        with open(self.test_filename, "rb") as f:
            response = self.client.post(
                "/documents",
                data={"subject": "Duplicate Case File"},
                files={"file": (self.test_filename, f, "text/plain")}
            )
            
        self.assertEqual(response.status_code, 400)
        self.assertIn("already exists", response.json()["detail"])