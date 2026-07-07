import streamlit as st
import os

st.set_page_config(page_title="Sherlock Assistant", layout="wide")

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
    st.title("List of Cases")
    st.write("This is the database case inventory library.")

elif page == "Quick Case Submission":
    st.title("Quick Case Submission")
    st.write("This is where new evidence files are uploaded.")