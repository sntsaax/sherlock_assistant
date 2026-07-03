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

class Test_FR_3_3(unittest.TestCase):

    def test_similarity_search_and_retrieval(self):
        """FR-3.3: Verify that querying the database returns the most relevant chunks."""
        filename = "temp_fr33_test.txt"
        case_id = "test_case_777"
        
        with open(filename, "w", encoding="utf-8") as f:
            f.write(
                "Clue 1: The missing diamond was hidden inside the antique grandfather clock. "
                "Clue 2: The gardener was planting red roses near the front gate all morning."
            )

        try:
            # Ingest the file with FR-3.2
            from rag.rag_engine import add_to_vector_store, query_vector_store
            add_to_vector_store(filename, case_id)
            
            # Query something specific
            retrieved_chunks = query_vector_store("Where is the missing diamond?", case_id, n_results=1)
            
            self.assertGreater(len(retrieved_chunks), 0)
            self.assertIn("grandfather clock", retrieved_chunks[0])
            
        finally:
            if os.path.exists(filename):
                os.remove(filename)
                
            from rag.rag_engine import chroma_client
            try:
                collection = chroma_client.get_collection(name="sherlock_cases")
                collection.delete(where={"case_id": case_id})
            except Exception:
                pass

class Test_FR_3_4(unittest.TestCase):

    def test_context_augmented_prompt_generation(self):
        """FR-3.4: Verify the constructed prompt injects context and rules correctly."""
        filename = "temp_fr34_test.txt"
        case_id = "test_case_555"
        
        with open(filename, "w", encoding="utf-8") as f:
            f.write("Evidence item: The footprint found in the mud belongs to a size 11 Goodyear boot.")

        try:
            # Ingest the test file with FR-3.2
            from rag.rag_engine import add_to_vector_store, generate_augmented_prompt
            add_to_vector_store(filename, case_id)
            
            # Generate the prompt for the user's query
            final_prompt = generate_augmented_prompt("What size was the boot footprint?", case_id)
            
            self.assertIn("You are Sherlock, an expert investigative digital assistant.", final_prompt)
            self.assertIn("size 11 Goodyear boot", final_prompt)
            self.assertIn("What size was the boot footprint?", final_prompt)
            
        finally:
            if os.path.exists(filename):
                os.remove(filename)
                
            from rag.rag_engine import chroma_client
            try:
                collection = chroma_client.get_collection(name="sherlock_cases")
                collection.delete(where={"case_id": case_id})
            except Exception:
                pass