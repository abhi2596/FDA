import streamlit as st
import shutil
import os
from parse_and_summarize import document_summary

# Add more import statements for other document types as needed

def main():
    st.sidebar.title("Document Type")
    page = st.sidebar.selectbox(
        "Select a document type",
        ["Tax Declaration", "Invoices", "Agreements", "CMR/Waybills", "Custom Declarations", "Acceptance and Holdover Certificate"]
    )
    page_selector(page)


def page_selector(page):
    st.title(page)
    uploaded_files = st.file_uploader(f"Upload a {page} Form", accept_multiple_files=True)
    if len(uploaded_files) != 0:
        response = None
        page = page.replace(" ", "_").upper()
        directory_name = f"{page}_files"
        os.makedirs(directory_name, exist_ok=True)
        for file in uploaded_files:
            with open(f"{directory_name}/{file.name}","wb") as f:
                f.write(file.read())
        response = document_summary(directory_name,page)
        if response is not None:
            st.markdown(response)
            shutil.rmtree(directory_name)
            
if __name__ == "__main__":
    main()
