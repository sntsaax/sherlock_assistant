import os
import uuid
import shutil
from datetime import datetime
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
    # Reject duplicates
    for record in metadata_db:
        if record["filename"] == file.filename:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Duplicate file error: '{file.filename}' already exists."
            )

    # Extract metadata and generate a unique ID
    generated_id = str(uuid.uuid4())
    current_date = datetime.now().strftime("%Y-%m-%d")
    
    # Define a temporary save path
    temp_dir = "temp_uploads"
    os.makedirs(temp_dir, exist_ok=True)
    file_path = os.path.join(temp_dir, file.filename)
    
    try:
        # Save file to disk temporarily
        with open(file_path, "wb") as buffer:
            shutil_copy = file.file.read()
            buffer.write(shutil_copy)
            
        add_to_vector_store(file_path, generated_id)
        
    except Exception as e:
        if os.path.exists(file_path):
            os.remove(file_path)
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing file in RAG engine: {str(e)}"
        )
    finally:
        # Clean up the file from disk
        if os.path.exists(file_path):
            os.remove(file_path)

    # 5. Save the metadata record into local table
    metadata_record = {
        "id": generated_id,
        "filename": file.filename,
        "subject": subject,
        "date_added": current_date
    }
    metadata_db.append(metadata_record)

    # Return the metadata object to UI
    return metadata_record


@app.get("/documents", status_code=status.HTTP_200_OK)
async def get_all_documents():
    """FR-2.2: Retrieve"""
    return metadata_db

@app.delete("/documents/{case_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(case_id: str):
    """FR-2.2: Delete"""
    global metadata_db
    
    # Search for the record
    record_to_delete = None
    for record in metadata_db:
        if record["id"] == case_id:
            record_to_delete = record
            break
            
    # If it doesn't exist, fail
    if not record_to_delete:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Case with ID {case_id} not found."
        )
        
    # Remove from database array
    metadata_db.remove(record_to_delete)
    
    return
