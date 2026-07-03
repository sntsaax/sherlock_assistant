import os
from pypdf import PdfReader
import chromadb
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
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

def query_vector_store(query_text: str, case_id: str, n_results: int = 3) -> list[str]:

    """FR-3.3"""
    collection = chroma_client.get_or_create_collection(name="sherlock_cases")
    
    # Query the collection
    results = collection.query(
        query_texts=[query_text],
        n_results=n_results,
        where={"case_id": case_id}
    )
    
    # Return a list of lists for documents
    if results and results.get("documents"):
        return results["documents"][0]
    
    return []

def generate_augmented_prompt(query_text: str, case_id: str) -> str:
    
    """FR-3.4"""
    # FR-3.3 to find the matching context blocks
    retrieved_chunks = query_vector_store(query_text, case_id, n_results=3)
    
    # Join the blocks
    context_str = "\n---\n".join(retrieved_chunks) if retrieved_chunks else "No relevant evidence found."
    
    # 3. Build the prompt
    prompt = f"""You are Sherlock, an expert investigative digital assistant. 
        Your goal is to answer the user's question using ONLY the provided case evidence below. 

        CRITICAL RULES:
        1. Ground your answer strictly in the provided evidence.
        2. If the evidence does not contain the answer, state clearly: "I don't have enough evidence to answer that."
        3. Do not make up facts, assumptions, or external details.

        ---
        RETRIEVED EVIDENCE:
        {context_str}
        ---

        USER QUESTION: {query_text}

        SHERLOCK'S ANALYSIS:"""
    
    return prompt

from openai import OpenAI

def generate_sherlock_answer(query_text: str, case_id: str) -> str:
    
    """FR-3.5"""
    # Generate the prompt from FR-3.4
    full_prompt = generate_augmented_prompt(query_text, case_id)
    
    # Initialize the client
    client = OpenAI()
    
    response = client.chat.completions.create(
        model="gpt-4o-mini",  # As in Thesis, cheaper
        messages=[
            {"role": "user", "content": full_prompt}
        ],
        temperature=0.0  # 0 for strict analytical responses
    )
    
    return response.choices[0].message.content