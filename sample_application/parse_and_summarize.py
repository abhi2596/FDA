from llama_parse import LlamaParse 
import os, tiktoken, requests, nest_asyncio,filetype,shutil
import streamlit as st 
from pdf_to_image import convert_pdf_to_image,get_image_prompt

nest_asyncio.apply()

def summarize(prompt,system_prompt=None,img_prompt=None):
    api_key = st.secrets["OPENAI_API_KEY"]
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    if img_prompt is not None:
        prompt = [{
            "type":"text",
            "text":prompt
        }]
        prompt.extend(img_prompt)
    messages = []
    if system_prompt is not None:
        messages.append({"role":"system","content":prompt})
    messages.append({"role":"user","content":prompt})
    payload = {
        "model": "gpt-4o",
        "messages": messages,
        "temperature":0
    }
    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
    response = response.json()
    return response["choices"][0]["message"]["content"]

def document_summary(directory_name,document_type):
    summary_of_documents = []
    with st.spinner("Summarizing Documents"):
        os.makedirs("img_files",exist_ok=True)
        for file_name in sorted(os.listdir(directory_name)):
            if file_name.endswith(".pdf"):
                img_dir = convert_pdf_to_image(os.path.join(directory_name,file_name))
                img_prompt = get_image_prompt(img_dir)
            elif filetype.is_image(os.path.join(directory_name,file_name)):
                img_prompt = get_image_prompt(os.path.join(directory_name,file_name))
            system_prompt = st.secrets.get(f'{document_type}_PROMPT')
            prompt = f"Extract the data in this {document_type} and output in markdown format"
            summary_of_documents.append(summarize(prompt,system_prompt,img_prompt))
        shutil.rmtree("img_files")
    total_summary = "\n".join(summary_of_documents)
    with st.spinner("Final Summary of Documents"):
        summary_prompt = st.secrets.get("SUMMARY_PROMPT").format(summary_of_documents=total_summary,document_type=document_type)
        document_summary = summarize(summary_prompt)
    return document_summary,summary_of_documents

if __name__ == "__main__":
    import argparse 
    parser = argparse.ArgumentParser()
    parser.add_argument("--document_type", type=str, choices=['invoices', 'tax_declaration'], help="Specify document type")
    args = parser.parse_args()
    print(document_summary(args.document_path, args.document_type))
