import unittest
import os
from rag.rag_engine import load_and_chunk_document

class Test_FR_3_1(unittest.TestCase):

    def test_text_extraction_and_chunking(self):
        """Verify that files are successfully read and split into blocks."""
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