import requests
from bs4 import BeautifulSoup
from llama_index.core import SimpleDirectoryReader, VectorStoreIndex
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.ollama import Ollama
import time
import os

# Define output file path
OUTPUT_FILE_PATH = r"C:\temp\web_content.txt"

def scrape_webpage(url: str) -> str:
    """
    Scrape the content from the given URL and save it to a file.
    """
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
            print(f"An error occurred while scraping: {e}")
            return None
        else:
            # Scrape the content from <p> tags
            soup = BeautifulSoup(response.text, "html.parser")
            text = ' '.join([p.text for p in soup.find_all("p")])  # Extract all <p> text

            # Create the output directory if it doesn't exist
            output_dir = os.path.dirname(OUTPUT_FILE_PATH)
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)

            # Limit to first 1000 characters for content size
            limited_text = text[:1000]  
            with open(OUTPUT_FILE_PATH, "w", encoding="utf-8") as f:
                f.write(limited_text)
            print(f"✅ Fetched and saved content from {url}")
            return OUTPUT_FILE_PATH

def load_index(file_path: str) -> VectorStoreIndex:
    """
    Load the index from the saved file and create a new index.
    """
    try:
        embed_model = HuggingFaceEmbedding(model_name="sentence-transformers/all-MiniLM-L6-v2")
        reader = SimpleDirectoryReader(input_files=[file_path])
        documents = reader.load_data()
        if len(documents) == 0:
            print("❌ No documents found to index!")
            return None
        print(f"📂 Loaded {len(documents)} document(s) into the index.")
        # Create the index from documents
        return VectorStoreIndex.from_documents(documents, embed_model=embed_model)
    except Exception as e:
        print(f"Error loading index: {e}")
        return None

def get_answer_from_url(url: str, question: str) -> str:
    """
    Scrape the webpage, load the index, and query the model for an answer.
    """
    try:
        print("📄 Scraping webpage", url)
        file_path = scrape_webpage(url)
        if not file_path:
            return "Failed to fetch webpage."

        print("💡 Loading index from", file_path)
        index = load_index(file_path)
        if not index:
            return "Failed to load index."

        # Use Ollama with a supported model
        llm = Ollama(model="mistral")  # Ensure this model is supported
        query_engine = index.as_query_engine(llm=llm)

        print("🧠 Querying model for the question:", question)
        response = query_engine.query(question)

        if response:
            print(f"✅ Answer found: {response.response}")
            return response.response
        else:
            print("❌ No relevant answer found.")
            return "No relevant answer found."
    except Exception as e:
        print(f"An error occurred: {e}")
        return "Error fetching answer."
