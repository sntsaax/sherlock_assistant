import os
from pypdf import PdfReader
import chromadb

chroma_client = chromadb.PersistentClient(path="./chroma_db")

def load_and_chunk_document(file_path: str) -> list[str]:
    """FR-3.1"""
    raw_text = ""
    
    # Check if the file is a PDF
    if file_path.endswith('.pdf'):
        reader = PdfReader(file_path)
        for page in reader.pages:
            text = page.extract_text()
            if text:
                raw_text += text + "\n"
                
    # Or treat it as a plain text file (.txt)
    else:
        with open(file_path, 'r', encoding='utf-8') as f:
            raw_text = f.read()
  
    # Chop the text into chunks
    chunk_size = 500
    overlap = 100 
    chunks = []
    
    for i in range(0, len(raw_text), chunk_size - overlap):
        chunk = raw_text[i:i + chunk_size]
        chunks.append(chunk)
        
    return chunks

def add_to_vector_store(file_path: str, case_id: str):
    """FR-3.2"""

    collection = chroma_client.get_or_create_collection(name="sherlock_cases")
    
    chunks = load_and_chunk_document(file_path)
    chunk_ids = [f"{case_id}_chunk_{i}" for i in range(len(chunks))]
    metadata_tags = [{"case_id": case_id} for _ in chunks]
    
    collection.add(
        documents=chunks,
        metadatas=metadata_tags,
        ids=chunk_ids
    )