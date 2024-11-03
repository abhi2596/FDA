import streamlit as st
import shutil
import os
from parse_and_summarize import document_summary


@st.fragment
def display_summaries(uploaded_files,individual_summaries,main_summary):
    st.header("Individual Summaries")
    for (file, summary) in zip(uploaded_files, individual_summaries):
        if st.checkbox(f"Show {file.name} Summary",key=file.name):
            st.markdown(summary)
    
    st.header("Total Summary")
    if st.checkbox(f"Show total summary",key="total"):
        st.markdown(main_summary)

def main():
    st.sidebar.title("Document Type")
    page = st.sidebar.selectbox(
        "Select a document type",
        ["Tax Declaration", "Invoices", "Agreements", "CMR/Waybills", "Custom Declarations", "Acceptance and Holdover Certificate"]
    )
    page_selector(page)

def page_selector(page):
    uploaded_files = st.file_uploader(f"Upload a {page} Form", accept_multiple_files=True)
    if len(uploaded_files) != 0:
        if page == "CMR/Waybills":
            page = page.replace("/","_").upper()
        else:
            page = page.replace(" ", "_").upper()
        directory_name = f"{page}_files"
        os.makedirs(directory_name, exist_ok=True)
        
        # Save uploaded files
        for file in uploaded_files:
            with open(f"{directory_name}/{file.name}", "wb") as f:
                f.write(file.read())
        
        # Get summaries
        main_summary, individual_summaries = document_summary(directory_name, page)
        display_summaries(uploaded_files,individual_summaries,main_summary)
        # Cleanup
        shutil.rmtree(directory_name)

if __name__ == "__main__":
    main()