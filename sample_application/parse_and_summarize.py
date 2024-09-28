from llama_parse import LlamaParse 
import os,tiktoken,requests,nest_asyncio
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

def tax_declaration_summary(tax_declaration_path):
    with st.spinner("Parsing PDF files"):
        parser = LlamaParse(api_key=st.secrets["LLAMA_CLOUD_API_KEY"])
        tax_summary = []
        documents = parser.load_data([os.path.join(tax_declaration_path,file_name) for file_name in os.listdir(tax_declaration_path)])
        text = ""
        for document in documents:
            text += document.text 
    with st.spinner("Summarizing Documents"):
        prompt = f"""Extract the following information from this text {text}
                1) What are the income sources (e.g. salary, capital gain, income from property selling activities, from self-employment etc.), 
                2) What is the amount of each income source, 
                3) What is the currencies of income sources, 
                4) Person name of this declaration; 
                5) Country, 
                6) Which companies and/or persons are payers?, 
                7) Year"""
        summary_of_documents = token_count_and_summarize(prompt)
        prompt = f"""The following information was summarized from different tax declaration documents {summary_of_documents}
                    Summarize this in logical paragraphs that explains what we see from these documents. 
                    Do not make any calculations.Give only facts in chronological order"""
        tax_summary = token_count_and_summarize(prompt,2048)
    return tax_summary

if __name__ == "__main__":
    import argparse 
    parser = argparse.ArgumentParser()
    parser.add_argument("--tax_path",type=str,help="Provide path for tax documents folder")
    args = parser.parse_args()
    print(tax_declaration_summary(args.tax_path))