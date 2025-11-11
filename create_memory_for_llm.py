from langchain_community.document_loaders import PyPDFLoader, DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
import google.generativeai as genai
import os

## Uncomment the following files if you're not using pipenv as your virtual environment manager
from dotenv import load_dotenv
load_dotenv()

# Step 0: Configure Gemini API
def configure_gemini():
    """Configure Gemini API with your API key"""
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY not found in environment variables")
    
    genai.configure(api_key=api_key)
    return genai

# Initialize Gemini
gemini_client = configure_gemini()

# Step 1: Load raw PDF(s)
DATA_PATH = "data/"

def load_pdf_files(data):
    loader = DirectoryLoader(data,
                             glob='*.pdf',
                             loader_cls=PyPDFLoader)
    
    documents = loader.load()
    return documents

documents = load_pdf_files(data=DATA_PATH)
print("Length of PDF pages: ", len(documents))

# Step 2: Create Chunks
def create_chunks(extracted_data):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50
    )
    text_chunks = text_splitter.split_documents(extracted_data)
    return text_chunks

text_chunks = create_chunks(extracted_data=documents)
print("Length of Text Chunks: ", len(text_chunks))

# Step 3: Create Vector Embeddings using Gemini
def get_embedding_model():
    """Get embedding model - you can choose between HuggingFace or Gemini"""
    # Option 1: Continue using HuggingFace (recommended for now as Gemini embeddings have separate API)
    embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    return embedding_model

def get_gemini_embeddings(texts):
    """Get embeddings using Gemini's embedding model"""
    try:
        # Using Gemini's embedding model
        embedding_model = "models/embedding-001"
        embeddings = []
        
        for text in texts:
            result = genai.embed_content(
                model=embedding_model,
                content=text,
                task_type="retrieval_document"
            )
            embeddings.append(result['embedding'])
        
        return embeddings
    except Exception as e:
        print(f"Error getting Gemini embeddings: {e}")
        return None

# Step 4: Enhanced function to store embeddings with Gemini integration
def create_vector_store_with_gemini(text_chunks, use_gemini_embeddings=False):
    """Create vector store with option to use Gemini embeddings"""
    
    if use_gemini_embeddings:
        # Extract text from documents
        texts = [chunk.page_content for chunk in text_chunks]
        
        # Get Gemini embeddings
        gemini_embeddings = get_gemini_embeddings(texts)
        
        if gemini_embeddings:
            # Create FAISS index with custom embeddings
            from langchain_community.vectorstores.utils import DistanceStrategy
            from langchain_community.vectorstores import FAISS
            
            # Create FAISS index manually with Gemini embeddings
            db = FAISS.from_embeddings(
                text_embeddings=list(zip(texts, gemini_embeddings)),
                embedding=HuggingFaceEmbeddings(),  # Dummy embedding for interface
                distance_strategy=DistanceStrategy.COSINE
            )
            return db
        else:
            print("Falling back to HuggingFace embeddings due to Gemini API issues")
    
    # Default: Use HuggingFace embeddings
    embedding_model = get_embedding_model()
    db = FAISS.from_documents(text_chunks, embedding_model)
    return db

# Step 5: Query using Gemini
def query_with_gemini(query, db, k=3):
    """Query the vector database and use Gemini for final response"""
    
    # Step 1: Retrieve relevant chunks from vector store
    relevant_docs = db.similarity_search(query, k=k)
    context = "\n\n".join([doc.page_content for doc in relevant_docs])
    
    # Step 2: Use Gemini to generate response based on context
    try:
        # Initialize Gemini model
        model = genai.GenerativeModel('gemini-pro')
        
        prompt = f"""Based on the following context, please answer the question. 
        If the answer cannot be found in the context, please say so.

        Context:
        {context}

        Question: {query}

        Answer:"""
        
        response = model.generate_content(prompt)
        return {
            "answer": response.text,
            "source_documents": relevant_docs
        }
        
    except Exception as e:
        return {
            "answer": f"Error querying Gemini: {str(e)}",
            "source_documents": relevant_docs
        }

# Step 6: Main execution
DB_FAISS_PATH = "vectorstore/db_faiss"

# Create vector store (using HuggingFace embeddings by default)
db = create_vector_store_with_gemini(text_chunks, use_gemini_embeddings=False)
db.save_local(DB_FAISS_PATH)
print("Vector store created and saved successfully!")

# Example usage
def chat_with_pdf():
    """Interactive chat function using Gemini"""
    # Load the saved vector store
    embedding_model = get_embedding_model()
    db = FAISS.load_local(DB_FAISS_PATH, embedding_model, allow_dangerous_deserialization=True)
    
    print("Chat with your PDF! Type 'exit' to quit.")
    
    while True:
        query = input("\nYour question: ")
        if query.lower() == 'exit':
            break
        
        response = query_with_gemini(query, db)
        print(f"\nAnswer: {response['answer']}")
        print(f"\nSources: {len(response['source_documents'])} relevant documents found")

# Uncomment to run interactive chat
# chat_with_pdf()

# Alternative: Simple query example
def simple_query_example():
    """Example of a single query"""
    embedding_model = get_embedding_model()
    db = FAISS.load_local(DB_FAISS_PATH, embedding_model, allow_dangerous_deserialization=True)
    
    query = "What is the main topic of the document?"
    response = query_with_gemini(query, db)
    
    print(f"Question: {query}")
    print(f"Answer: {response['answer']}")
    print(f"Sources found: {len(response['source_documents'])}")

# Run example
simple_query_example()