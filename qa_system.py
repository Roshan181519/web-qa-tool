import requests
from bs4 import BeautifulSoup
from llama_index.core import SimpleDirectoryReader, VectorStoreIndex
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.ollama import Ollama
import time
import os

def scrape_webpage(url: str, output_path: str) -> str:
    max_retries = 3
    retry_count = 0
    while retry_count < max_retries:
        try:
            headers = {"User-Agent": "Mozilla/5.0"}
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
        except requests.exceptions.Timeout:
            print("Timeout occurred, retrying...")
            time.sleep(2)  # Wait before retrying
            retry_count += 1
        except requests.exceptions.RequestException as e:
            print(f"An error occurred: {e}")
            return None
        else:
            soup = BeautifulSoup(response.text, "html.parser")
            text = ' '.join([p.text for p in soup.find_all("p")])  # Extract all <p> text

            output_dir = os.path.dirname(output_path)
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)

            # Limit text to first 1000 characters
            limited_text = text[:1000]  
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(limited_text)
            print("✅ Fetched and saved content!")
            return output_path

def load_index(file_path: str) -> VectorStoreIndex:
    embed_model = HuggingFaceEmbedding(model_name="sentence-transformers/all-MiniLM-L6-v2")  # Local embeddings
    reader = SimpleDirectoryReader(input_files=[file_path])
    documents = reader.load_data()
    return VectorStoreIndex.from_documents(documents, embed_model=embed_model)

def get_answer_from_url(url: str, question: str, output_path: str) -> str:
    try:
        print("📄 Scraping webpage", url)
        file_path = scrape_webpage(url, output_path)
        if not file_path:
            return "Failed to fetch webpage."

        print("💡 Loading index from", file_path)
        index = load_index(file_path)
        
        # Use Ollama with a supported model
        llm = Ollama(model="llama3")  # Ensure this model is supported
        query_engine = index.as_query_engine(llm=llm)

        print("🧠 Querying model for the question:", question)
        response = query_engine.query(question)
        return response.response if response else "No relevant answer found."
    except Exception as e:
        print(f"An error occurred: {e}")
        return "Failed to generate answer."

if __name__ == "__main__":
    url = input("🔍 Enter webpage URL: ")
    question = input("❓ Ask a question about the webpage: ")
    output_path = r"C:\temp\web_content.txt"
    
    print("\n📌 Answer:", get_answer_from_url(url, question, output_path))
