import os
import shutil
from datetime import date
from fastapi import FastAPI, UploadFile, Form, HTTPException, status

# vector store function from rag_engine.py
from src.rag.rag_engine import add_to_vector_store

app = FastAPI(title="Sherlock Backend - FR-2.1")

# Python list serving as local database table (FR-2.1)
metadata_db = []

@app.post("/documents", status_code=status.HTTP_201_CREATED)
async def upload_document(
    subject: str = Form(...), 
    file: UploadFile = Form(...)
):
    # Reject invalid file extensions format (FR-2.1)
    if not (file.filename.endswith('.pdf') or file.filename.endswith('.txt')):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Invalid file type. Only PDF and .txt files are allowed."
        )
    
