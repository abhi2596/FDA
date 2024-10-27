from llama_parse import LlamaParse 
import os, tiktoken, requests, nest_asyncio,shutil
import streamlit as st 

nest_asyncio.apply()

def token_count_and_summarize(prompt,max_tokens=300):
    num_of_tokens = get_token_count(prompt)
    if num_of_tokens < 128000:
        return summarize(prompt,max_tokens)
    else:
        pass

def get_token_count(text):
    encode = tiktoken.encoding_for_model("gpt-4o-mini") 
    return len(encode.encode(text)) 

def summarize(prompt,max_tokens=300):
    api_key = st.secrets["OPENAI_API_KEY"]
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    payload = {
        "model": "gpt-4o-mini",
        "messages": [
            {"role":"system","content":"You are a bank compliance officer"},
            {
                "role": "user",
                "content": prompt
            }
        ],
        "max_tokens": max_tokens
    }
    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
    response = response.json()
    return response["choices"][0]["message"]["content"]

def document_summary(directory_name,document_type):
    with st.spinner("Parsing PDF files"):
        parser = LlamaParse(api_key=st.secrets["LLAMA_CLOUD_API_KEY"])
        document_text = []
        for file_name in sorted(os.listdir(directory_name)):
            documents = parser.load_data([os.path.join(directory_name, file_name)])
            document_text.append("".join([document.text for document in documents]))
    
    with st.spinner("Summarizing Documents"):
        summary_of_documents = []
        for document in document_text:
            prompt = st.secrets.get(f'{document_type}_PROMPT').format(text=document)
            summary_of_documents.append(token_count_and_summarize(prompt))

    total_summary = "\n".join(summary_of_documents)
    with st.spinner("Final Summary of Documents"):
        summary_prompt = st.secrets.get("SUMMARY_PROMPT").format(summary_of_documents=total_summary,document_type=document_type)
        document_summary = token_count_and_summarize(summary_prompt)
    return document_summary,summary_of_documents

if __name__ == "__main__":
    import argparse 
    parser = argparse.ArgumentParser()
    parser.add_argument("--document_type", type=str, choices=['invoices', 'tax_declaration'], help="Specify document type")
    args = parser.parse_args()
    print(document_summary(args.document_path, args.document_type))
