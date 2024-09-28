import streamlit as st,shutil,os
from parse_and_summarize import tax_declaration_summary


st.title("Tax Declaration Form")
uploaded_files = st.file_uploader("Upload a Tax Declaration Form",accept_multiple_files=True)

if len(uploaded_files) != 0:
    for file in uploaded_files:
        with open(f"files/{file.name}","wb") as f:
            f.write(file.read())
    response = tax_declaration_summary("files")
    if response is not None:
        st.markdown(response)
    for filename in os.listdir("files"):
        file_path = os.path.join("files", filename)
        os.remove(file_path)
    
    