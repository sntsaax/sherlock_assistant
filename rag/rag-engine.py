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