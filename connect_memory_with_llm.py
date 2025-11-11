import os
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

print("🔧 Loading dependencies...")

try:
    from langchain_community.vectorstores import FAISS
    from langchain_huggingface import HuggingFaceEmbeddings
    print("✅ All dependencies loaded successfully!")
except ImportError as e:
    print(f"❌ Missing dependency: {e}")
    print("Please install: uv add langchain-community huggingface-hub sentence-transformers faiss-cpu")
    exit(1)

def setup_gemini():
    """Setup Gemini API"""
    GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")
    if not GOOGLE_API_KEY:
        print("❌ GOOGLE_API_KEY not found in .env file")
        print("Please add: GOOGLE_API_KEY=your_actual_key_here")
        return None
    
    try:
        genai.configure(api_key=GOOGLE_API_KEY)
        model = genai.GenerativeModel('gemini-pro')
        print("✅ Gemini configured successfully!")
        return model
    except Exception as e:
        print(f"❌ Error setting up Gemini: {e}")
        return None

def load_vector_store():
    """Load FAISS vector store"""
    DB_FAISS_PATH = "vectorstore/db_faiss"
    
    try:
        embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
        db = FAISS.load_local(DB_FAISS_PATH, embedding_model, allow_dangerous_deserialization=True)
        print("✅ FAISS vector database loaded!")
        return db
    except Exception as e:
        print(f"❌ Error loading FAISS database: {e}")
        return None

def ask_question(model, db, query):
    """Ask question using RAG pattern"""
    # Retrieve relevant documents
    docs = db.similarity_search(query, k=3)
    
    # Build context from documents
    context = "\n\n".join([f"Document {i+1}:\n{doc.page_content}" for i, doc in enumerate(docs)])
    
    # Create prompt
    prompt = f"""Based on the following context, please answer the question. 
If the answer cannot be found in the context, say "I don't have enough information to answer this question."

Context:
{context}

Question: {query}

Answer:"""
    
    try:
        response = model.generate_content(prompt)
        return response.text, docs
    except Exception as e:
        return f"Error: {str(e)}", docs

def main():
    print("🚀 Starting Gemini RAG System...")
    
    # Setup Gemini
    model = setup_gemini()
    if not model:
        return
    
    # Load vector store
    db = load_vector_store()
    if not db:
        return
    
    # Interactive chat
    print("\n" + "="*50)
    print("💬 Chat with your documents! Type 'exit' to quit.")
    print("="*50)
    
    while True:
        try:
            user_query = input("\n🤔 Your question: ").strip()
            
            if user_query.lower() in ['exit', 'quit', 'bye']:
                print("👋 Goodbye!")
                break
                
            if not user_query:
                print("⚠️ Please enter a question")
                continue
            
            print("🔄 Processing your question...")
            
            # Get response
            answer, source_docs = ask_question(model, db, user_query)
            
            print("\n" + "📝 ANSWER: " + "="*40)
            print(answer)
            
            print("\n" + "🔍 SOURCES: " + "="*39)
            for i, doc in enumerate(source_docs, 1):
                print(f"\n📄 Source {i}:")
                print(f"   📁 File: {doc.metadata.get('source', 'Unknown')}")
                print(f"   📄 Page: {doc.metadata.get('page', 'Unknown')}")
                print(f"   📝 Content: {doc.page_content[:200]}...")
                
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()