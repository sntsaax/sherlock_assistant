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

    def test_fr_2_2_get_all_documents(self):
        """FR-2.2: Verify GET /documents returns the complete inventory array."""
        # Seed the database array with a dummy record
        mock_record = {
            "id": "test-uuid-123",
            "filename": "old_case.txt",
            "subject": "The Red-Headed League",
            "date_added": "2026-07-04"
        }
        metadata_db.append(mock_record)
        
        response = self.client.get("/documents")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 1)
        self.assertEqual(response.json()[0]["id"], "test-uuid-123")

    def test_fr_2_2_delete_document_success(self):
        """FR-2.2: Verify DELETE /documents/{id} removes the case from memory."""
        mock_record = {
            "id": "delete-me-uuid",
            "filename": "temp.txt",
            "subject": "Temporary Clue",
            "date_added": "2026-07-04"
        }
        metadata_db.append(mock_record)
        
        # Ensure it exists before deletion
        self.assertEqual(len(metadata_db), 1)
        
        # Execute deletion
        response = self.client.delete("/documents/delete-me-uuid")
        self.assertEqual(response.status_code, 204)
        self.assertEqual(len(metadata_db), 0)

    def test_fr_2_2_delete_document_not_found(self):
        """FR-2.2: Verify deleting a non-existent ID returns a 404 Error."""
        response = self.client.delete("/documents/fake-missing-id")
        self.assertEqual(response.status_code, 404)