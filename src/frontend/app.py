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
    st.title("Interactive Chat Feed")

# FR-1.5 + 1.6: Interactive Chat Feed (Home Page View)

    cases = get_backend_cases()
    
    if cases is None:
        st.error("Cannot connect to backend server. Ensure Uvicorn is running.")
    elif not cases:
        st.warning("No active case files loaded. Go to 'Quick Case Submission' to upload evidence first.")
    else:
        # Context binding selection
        options_map = {f"{c['filename']} (ID: {c['id'][:8]})": c['id'] for c in cases}
        selected_label = st.selectbox("Select Active Case Context:", list(options_map.keys()))
        selected_case_id = options_map[selected_label]
        
        st.write("---")
        
        # Initialize in-memory session chat history list if it doesn't exist
        if "chat_history" not in st.session_state:
            st.session_state.chat_history = []
            
        # Scrollable chat window display container
        chat_container = st.container()
        with chat_container:
            for chat in st.session_state.chat_history:
                with st.chat_message(chat["role"]):
                    st.write(chat["content"])
                    
        # Main text input box
        if user_query := st.chat_input("Ask Sherlock a question about this case..."):
            
            # Display user message in feed
            with chat_container:
                with st.chat_message("user"):
                    st.write(user_query)
            st.session_state.chat_history.append({"role": "user", "content": user_query})
            
            # Forward the data to backend route (POST /query)
            try:
                payload = {"question": user_query, "case_id": selected_case_id}
                res = requests.post(f"{BACKEND_URL}/query", json=payload)
                
                if res.status_code == 200:
                    answer = res.json().get("answer", "")
                    
                    # Display the generated answer response in feed
                    with chat_container:
                        with st.chat_message("assistant"):
                            st.write(answer)
                    st.session_state.chat_history.append({"role": "assistant", "content": answer})
                else:
                    st.error("Backend error analyzing your question.")
            except Exception as e:
                st.error(f"Failed to communicate with RAG engine: {str(e)}")

elif page == "List of Cases":
    st.title("Case Library Dashboard")
    st.write("Active system memory records")

# (FR-1.4) Case Library Dashboard

    cases = get_backend_cases()
    
    if cases is None:
        st.error("Cannot connect to backend server. Ensure Uvicorn is running.")
    elif not cases:
        st.info("System memory workspace inventory is currently empty. Go upload an evidence file!")
    else:
        # Loop through each item in backend
        for record in cases:
            col1, col2 = st.columns([5, 1])
            
            with col1:
                # Displays details
                st.markdown(f"### 📄 `{record['filename']}`")
                st.markdown(
                    f"**Subject:** {record['subject']} | "
                    f"**Date Ingested:** {record['date_added']} | "
                    f"**Internal ID:** `{record['id']}`"
                )
            
            with col2:
                # Trigger deletion
                if st.button("Delete Case", key=record['id']):
                    try:
                        res = requests.delete(f"{BACKEND_URL}/documents/{record['id']}")
                        if res.status_code == 204:
                            st.success("Case removed!")
                            st.rerun()
                        else:
                            st.error("Failed to delete from inventory.")
                    except Exception as e:
                        st.error(f"Network failure: {str(e)}")
            st.markdown("---")

    
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