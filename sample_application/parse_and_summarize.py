from llama_parse import LlamaParse 
import os, tiktoken, requests, nest_asyncio,filetype,shutil
import streamlit as st 
from pdf_to_image import convert_pdf_to_image,get_image_prompt

nest_asyncio.apply()

def summarize(prompt,img_prompt=None):
    api_key = st.secrets["OPENAI_API_KEY"]
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    user_prompt = [{
        "type":"text",
        "text":prompt
    }]
    if img_prompt is not None:
        user_prompt.extend(img_prompt)
    payload = {
        "model": "gpt-4o",
        "messages": [
            {"role":"system","content":"You are a bank compliance officer"},
            {
                "role": "user",
                "content": user_prompt
            }
        ],
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
            prompt = st.secrets.get(f'{document_type}_PROMPT')
            summary_of_documents.append(summarize(prompt,img_prompt))
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
