import streamlit as st
import google.generativeai as genai
from datetime import datetime

def normalize(text):
    return text.strip().lower()

# 🔑 Configure Gemini API
genai.configure(api_key="AIzaSyAkc-nGXq2Mtgq_6qlKYmaVPdzpacV6u2k")

model = genai.GenerativeModel("models/gemini-2.5-flash")

# Streamlit page configuration
st.set_page_config(
    page_title="🎭 Local Culture Storytelling Bot",
    page_icon="📚",
    layout="wide"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .history-item {
        padding: 8px;
        margin: 5px 0;
        border-radius: 5px;
        background-color: #f0f2f6;
        border-left: 4px solid #ff6b6b;
        cursor: pointer;
    }
    .history-item:hover {
        background-color: #e6e9ef;
    }
    .history-time {
        font-size: 0.8em;
        color: #666;
    }
</style>
""", unsafe_allow_html=True)

st.title("🎭 Local Culture Storytelling Bot")
st.markdown("Ask about Indian festivals, food, or folk tales!")

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []

if "search_history" not in st.session_state:
    st.session_state.search_history = []

if "current_chat" not in st.session_state:
    st.session_state.current_chat = []

# Sidebar with tabs
st.sidebar.title("Navigation")

# Create tabs
tab1, tab2 = st.sidebar.tabs(["💡 Examples", "📜 History"])

# Tab 1: Example Questions
with tab1:
    st.header("💡 Example Questions")
    example_questions = [
        "Tell me a story from Karnataka",
        "What is the significance of Diwali?",
        "Famous food of Kerala?",
        "Tell me about Rajasthan's folk dances",
        "What is the story behind Holi?",
        "Traditional clothing of Tamil Nadu"
    ]

    for question in example_questions:
        if st.button(question, key=f"example_{question}", use_container_width=True):
            st.session_state.messages.append({"role": "user", "content": question})
            st.rerun()

# Tab 2: Search History
with tab2:
    st.header("📜 Search History")
    
    if not st.session_state.search_history:
        st.info("No search history yet. Start asking questions to build your history!")
    else:
        # Clear history button
        if st.button("🗑️ Clear All History", use_container_width=True):
            st.session_state.search_history = []
            st.rerun()
        
        st.subheader("Recent Searches")
        
        # Display history in reverse order (newest first)
        for i, history_item in enumerate(reversed(st.session_state.search_history)):
            col1, col2 = st.columns([3, 1])
            
            with col1:
                # Create a clickable history item
                if st.button(
                    f"**{history_item['query']}**\n\n"
                    f"_{history_item['timestamp']}_",
                    key=f"history_{i}",
                    use_container_width=True
                ):
                    # When clicked, add this query to current chat
                    st.session_state.messages.append({"role": "user", "content": history_item['query']})
                    st.rerun()
            
            with col2:
                # Delete button for each history item
                if st.button("❌", key=f"delete_{i}"):
                    st.session_state.search_history.pop(len(st.session_state.search_history) - 1 - i)
                    st.rerun()
            
            st.divider()

# Main chat area
# Display previous messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Cultural instruction
instruction = (
    "You are a Local Culture Storytelling Bot. "
    "Always answer about Indian culture, traditions, festivals, food, and folk tales. "
    "If asked something unrelated, gently redirect to Indian culture. "
    "Keep answers short, factual, and engaging."
)

# Handle user input
if prompt := st.chat_input("Ask about Indian culture..."):
    prompt = normalize(prompt)
    
    # Add to search history
    if prompt and prompt not in [item['query'] for item in st.session_state.search_history]:
        history_item = {
            "query": prompt,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "response_preview": ""  # We'll update this after getting the response
        }
        st.session_state.search_history.append(history_item)
    
    # Display user message
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    try:
        # Build conversation history
        history_for_gemini = []
        for msg in st.session_state.messages[:-1]:
            role = "user" if msg["role"] == "user" else "model"
            history_for_gemini.append({"role": role, "parts": [msg["content"]]})

        # Combine instruction + prompt for context
        full_prompt = f"{instruction}\nUser question: {prompt}"

        # Generate response
        response = model.generate_content(
            history_for_gemini + [{"role": "user", "parts": [full_prompt]}]
        )
        response_text = response.text
        
        # Update the latest history item with response preview
        if st.session_state.search_history:
            latest_item = st.session_state.search_history[-1]
            preview = response_text[:100] + "..." if len(response_text) > 100 else response_text
            latest_item["response_preview"] = preview

    except Exception as e:
        response_text = f"⚠️ Error: {str(e)}"

    # Display model response
    with st.chat_message("assistant"):
        st.markdown(response_text)

    st.session_state.messages.append({"role": "assistant", "content": response_text})
    
    # Force a rerun to update the history sidebar
    st.rerun()

# Additional sidebar information
st.sidebar.markdown("---")
st.sidebar.markdown("### ℹ️ About")
st.sidebar.info(
    "This bot helps you explore rich Indian cultural heritage through "
    "stories, facts, and information about festivals, food, and traditions."
)

# Display statistics in sidebar
if st.session_state.search_history:
    st.sidebar.markdown("### 📊 Statistics")
    st.sidebar.metric(
        "Total Searches", 
        len(st.session_state.search_history)
    )