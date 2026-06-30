import os
from pypdf import PdfReader

def load_and_chunk_document(file_path: str) -> list[str]:

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