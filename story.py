import streamlit as st
import google.generativeai as genai
from datetime import datetime
import time

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

# Professional CSS styling
st.markdown("""
<style>
    .sidebar-chat-item {
        padding: 8px 12px;
        margin: 2px 0;
        border-radius: 6px;
        border: none;
        background: transparent;
        text-align: left;
        width: 100%;
        font-size: 0.9em;
        cursor: pointer;
        transition: all 0.2s ease;
    }
    .sidebar-chat-item:hover {
        background-color: #f8f9fa;
        border-left: 2px solid #4f46e5;
    }
    .new-chat-btn {
        background: #e8f4f8;
        color: #1e40af;
        border: 1px solid #bfdbfe;
        padding: 10px 16px;
        border-radius: 8px;
        font-weight: 600;
        margin-bottom: 15px;
        transition: all 0.2s ease;
    }
    .new-chat-btn:hover {
        background: #dbeafe;
        border-color: #93c5fd;
    }
    .sidebar-header {
        font-size: 0.8em;
        font-weight: 600;
        color: #6b7280;
        margin: 15px 0 8px 0;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .trash-btn {
        background: #fee2e2;
        color: #dc2626;
        border: 1px solid #fecaca;
        padding: 4px 8px;
        border-radius: 4px;
        font-size: 0.7em;
        cursor: pointer;
        transition: all 0.2s ease;
    }
    .trash-btn:hover {
        background: #fecaca;
        transform: scale(1.1);
    }
    @keyframes dotAnimation {
        0%, 20% { opacity: 0; }
        50% { opacity: 1; }
        100% { opacity: 0; }
    }
    .thinking-dots {
        display: inline-block;
    }
    .thinking-dots::after {
        content: '...';
        animation: dotAnimation 1.5s infinite;
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

if "chat_sessions" not in st.session_state:
    st.session_state.chat_sessions = {
        "current": {
            "id": "current",
            "name": "New Chat",
            "messages": [],
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "preview": "Start a new conversation"
        }
    }

if "current_chat_id" not in st.session_state:
    st.session_state.current_chat_id = "current"

if "thinking" not in st.session_state:
    st.session_state.thinking = False

# Professional Sidebar
with st.sidebar:
    st.markdown("### Chat Assistant")
    
    # New Chat Button with pale professional color
    if st.button("New Chat", key="new_chat_btn", use_container_width=True):
        # Save current chat if it has messages
        if st.session_state.messages:
            chat_id = f"chat_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            # Generate short chat name from first message
            first_message = next((msg["content"] for msg in st.session_state.messages if msg["role"] == "user"), "Chat")
            # Extract key words for short name
            words = first_message.split()[:3]  # Take first 3 words
            chat_name = " ".join(words)
            if len(chat_name) > 20:
                chat_name = chat_name[:18] + "..."
            
            st.session_state.chat_sessions[chat_id] = {
                "id": chat_id,
                "name": chat_name,
                "messages": st.session_state.messages.copy(),
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "preview": st.session_state.messages[-1]["content"][:50] + "..." if st.session_state.messages else "New chat"
            }
        
        # Clear current chat
        st.session_state.messages = []
        st.session_state.current_chat_id = "current"
        st.session_state.chat_sessions["current"] = {
            "id": "current",
            "name": "New Chat",
            "messages": [],
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "preview": "Start a new conversation"
        }
        st.session_state.thinking = False
        st.rerun()
    
    st.markdown('<div class="sidebar-header">Chat History</div>', unsafe_allow_html=True)
    
    # Display Chat History
    chat_items = []
    
    # Add all chats except current empty one if it's empty
    for chat_id, chat_data in st.session_state.chat_sessions.items():
        if chat_id == "current" and not chat_data["messages"]:
            continue  # Skip empty current chat
        chat_items.append((chat_id, chat_data))
    
    # Sort by creation time (newest first)
    chat_items.sort(key=lambda x: x[1]["created_at"], reverse=True)
    
    if not chat_items:
        st.info("No chat history yet")
    else:
        # Display chat history items with delete buttons
        for chat_id, chat_data in chat_items:
            is_active = chat_id == st.session_state.current_chat_id
            
            # Create columns for chat name and delete button
            col1, col2 = st.columns([4, 1])
            
            with col1:
                # Chat item button - only show the short name
                if st.button(
                    chat_data['name'],
                    key=f"chat_{chat_id}",
                    use_container_width=True
                ):
                    st.session_state.current_chat_id = chat_id
                    st.session_state.messages = chat_data["messages"].copy()
                    st.session_state.thinking = False
                    st.rerun()
            
            with col2:
                # Small trash icon button
                if st.button("🗑️", key=f"delete_{chat_id}", help="Delete this chat"):
                    # Don't delete if it's the current active chat with messages
                    if chat_id == st.session_state.current_chat_id:
                        # Switch to new chat if deleting current
                        st.session_state.current_chat_id = "current"
                        st.session_state.messages = []
                        st.session_state.thinking = False
                    
                    del st.session_state.chat_sessions[chat_id]
                    st.rerun()

# Main chat area - Remove "New Chat" text from middle
current_chat_name = st.session_state.chat_sessions[st.session_state.current_chat_id]['name']
if current_chat_name != "New Chat":
    st.subheader(f"💬 {current_chat_name}")

# Display messages for current chat
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Show thinking message if processing
if st.session_state.thinking:
    with st.chat_message("assistant"):
        # Create a simple animated thinking message
        thinking_placeholder = st.empty()
        
        # Simple animation with updating text
        dots = ["", ".", "..", "..."]
        for i in range(12):  # Show for max 12 cycles (about 3 seconds)
            if not st.session_state.thinking:
                break
            thinking_placeholder.markdown(f"Thinking{dots[i % 4]}")
            time.sleep(0.25)

# Show empty state if no messages
if not st.session_state.messages and not st.session_state.thinking:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
        <div style='text-align: center; padding: 40px; color: #6b7280;'>
            <h3>🎭 Welcome to Culture Bot!</h3>
            <p>Start a conversation about Indian culture, festivals, food, or folk tales.</p>
        </div>
        """, unsafe_allow_html=True)

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
            "response_preview": ""
        }
        st.session_state.search_history.append(history_item)
    
    # Display user message
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Set thinking state
    st.session_state.thinking = True
    st.rerun()

# Generate response if thinking state is active
if st.session_state.thinking:
    try:
        # Build conversation history
        history_for_gemini = []
        for msg in st.session_state.messages[:-1]:  # Exclude the last user message
            role = "user" if msg["role"] == "user" else "model"
            history_for_gemini.append({"role": role, "parts": [msg["content"]]})

        # Combine instruction + prompt for context
        full_prompt = f"{instruction}\nUser question: {st.session_state.messages[-1]['content']}"

        # Generate response
        response = model.generate_content(
            history_for_gemini + [{"role": "user", "parts": [full_prompt]}]
        )
        response_text = response.text
        
        # Update search history with response preview
        if st.session_state.search_history:
            latest_item = st.session_state.search_history[-1]
            preview = response_text[:100] + "..." if len(response_text) > 100 else response_text
            latest_item["response_preview"] = preview

    except Exception as e:
        response_text = f"⚠️ Error: {str(e)}"

    # Display model response and clear thinking state
    with st.chat_message("assistant"):
        st.markdown(response_text)

    st.session_state.messages.append({"role": "assistant", "content": response_text})
    
    # Update current chat session
    current_chat = st.session_state.chat_sessions[st.session_state.current_chat_id]
    current_chat["messages"] = st.session_state.messages.copy()
    
    # Update chat name with short version if it's the first message
    if len(st.session_state.messages) == 2:  # user + assistant
        # Create short name from first 3 words
        words = st.session_state.messages[0]["content"].split()[:3]
        chat_name = " ".join(words)
        if len(chat_name) > 20:
            chat_name = chat_name[:18] + "..."
        current_chat["name"] = chat_name
    
    # Clear thinking state
    st.session_state.thinking = False
    
    # Force a rerun to update the sidebar and remove thinking message
    st.rerun()