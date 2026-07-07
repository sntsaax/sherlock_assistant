import streamlit as st
import requests

st.set_page_config(page_title="Sherlock Assistant", layout="wide")

BACKEND_URL = "http://127.0.0.1:8000"

# Helper for fetching cases from the backend
def get_backend_cases():
    try:
        response = requests.get(f"{BACKEND_URL}/documents")
        if response.status_code == 200:
            return response.json()
    except Exception:
        return None
    return []

# FR-1.1: Welcome page

logo_path = "sherlock_logo.png"

st.markdown("### *Welcome Sherrlock, an Investigative Digital Assistant*")
st.write("---")
st.write("Welcome, Detective. Use the system to analyze case evidence files strictly and securely.")


# FR-1.2: Sidebar Navigation

with st.sidebar:
    st.image("sherlock_logo.png", width=150)
    st.markdown("---")
    
    # Navigation Menu
    page = st.radio(
        "Navigation Menu",
        ["Home Page", "List of Cases", "Quick Case Submission"]
    )

# Render content based on selected page
if page == "Home Page":
    st.title("Home Page")
    st.write("This is the main landing workstation screen.")

elif page == "List of Cases":
    st.title("Case Library Dashboard")
    st.write("Active system memory records")
    
elif page == "Quick Case Submission":
    st.title("Quick Case Submission")
    st.write("This is where new evidence files are uploaded.")

# (FR-1.3) Case submission
    with st.form("upload_form", clear_on_submit=True):
        subject_input = st.text_input("Case Subject / Description:", placeholder="e.g., Alibi Verification")
        
        # Allow only PDF and TXT
        uploaded_file = st.file_uploader("Choose a Case File:", type=["txt", "pdf"])
        
        submit_btn = st.form_submit_button("Upload Evidence")
        
        if submit_btn:
            if not subject_input or not uploaded_file:
                st.error("Please provide both a subject description and an evidence file.")
            else:
                with st.spinner("Processing file and running RAG engine ingestion..."):
                    try:
                        # Repack data
                        multipart_files = {
                            "file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)
                        }
                        form_data = {"subject": subject_input}
                        
                        response = requests.post(f"{BACKEND_URL}/documents", files=multipart_files, data=form_data)
                        
                        if response.status_code == 201:
                            st.success(f"Success! '{uploaded_file.name}' has been safely ingested into ChromaDB.")
                        else:
                            error_detail = response.json().get("detail", "Upload rejected.")
                            st.error(f"Upload failed: {error_detail}")
                    except Exception as e:
                        st.error(f"Could not connect to FastAPI backend server: {str(e)}")