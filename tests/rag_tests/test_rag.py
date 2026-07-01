import unittest
import os
from rag.rag_engine import load_and_chunk_document
from rag.rag_engine import add_to_vector_store

class Test_FR_3_1(unittest.TestCase):

    def test_text_extraction_and_chunking(self):
        """FR-3.1:Verify that files are successfully read and split into blocks."""
        filename = "temp_fr31_test.txt"
        with open(filename, "w", encoding="utf-8") as f:
            f.write("This is a sample witness statement. It needs to be long enough to chunk.")

        try:
            chunks = load_and_chunk_document(filename)
            self.assertIsInstance(chunks, list)
            self.assertGreater(len(chunks), 0)
        finally:
            if os.path.exists(filename):
                os.remove(filename)

    if __name__ == "__main__":
        unittest.main()
    
class Test_FR_3_2(unittest.TestCase):

    def test_vector_storage_and_indexing(self):
        """FR-3.2: Verify chunks are successfully saved and indexed in ChromaDB."""
        filename = "temp_fr32_test.txt"
        case_id = "test_case_999"
        
        with open(filename, "w", encoding="utf-8") as f:
            f.write("The suspect was seen leaving the alleyway at exactly midnight.")

        try:
            add_to_vector_store(filename, case_id)
            
            # Reach directly into ChromaDB
            from rag.rag_engine import chroma_client
            collection = chroma_client.get_collection(name="sherlock_cases")
            
            results = collection.get(where={"case_id": case_id})
            
            self.assertGreater(len(results["ids"]), 0)
            self.assertEqual(results["metadatas"][0]["case_id"], case_id)
            
        finally:
            if os.path.exists(filename):
                os.remove(filename)
                
            try:
                collection.delete(where={"case_id": case_id})
            except Exception:
                pass