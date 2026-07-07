import os
import uuid
import shutil
from datetime import datetime
from fastapi import FastAPI, UploadFile, File, HTTPException, status
from pydantic import BaseModel

# vector store function from rag_engine.py
from src.rag.rag_engine import add_to_vector_store, generate_sherlock_answer

app = FastAPI(title="Sherlock Backend - FR-2.1")

# Python list serving as local database table (FR-2.1)
metadata_db = []

# Pydantic Schema
class QueryRequest(BaseModel):
    question: str
    case_id: str

@app.post("/documents", status_code=status.HTTP_201_CREATED)
async def upload_document(
    subject: str = File(...), 
    file: UploadFile = File(...)
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
            content = await file.read()
            buffer.write(content)
            
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

    # Save the metadata record into local table
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


@app.post("/query", status_code=status.HTTP_200_OK)
async def route_detective_query(payload: QueryRequest):
    """FR-2.3: Route detective question"""
    
    # Verify the case exists
    case_exists = any(record["id"] == payload.case_id for record in metadata_db)
    if not case_exists:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Query failed: Case ID {payload.case_id} does not exist in inventory."
        )
        
    try:
        # RAG loop
        ai_analysis = generate_sherlock_answer(payload.question, payload.case_id)
        
        # Return the response
        return {
            "case_id": payload.case_id,
            "question": payload.question,
            "answer": ai_analysis
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"RAG Engine execution failed: {str(e)}"
        )
