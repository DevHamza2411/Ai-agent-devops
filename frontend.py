import streamlit as st
import requests

# Set page layout and title
st.set_page_config(page_title="DevOps AI Agent", page_icon="🔧", layout="centered")
st.title("🔧 DevOps Log Analyzer Agent")
st.caption("Talk to your local Llama 3.2 agent to scan and analyze system logs.")

# Initialize session state for chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display previous chat messages from history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Accept user chat input
if user_query := st.chat_input("Ask something (e.g., Please analyze app.log)"):
    
    # 1. Display user message in chat message container
    st.session_state.messages.append({"role": "user", "content": user_query})
    with st.chat_message("user"):
        st.markdown(user_query)

    # 2. Display assistant response placeholder with a loading spinner
    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        
        try:
            # Send the question to your live FastAPI backend
            API_URL = "http://localhost:8000/v1/chat"
            payload = {"question": user_query}
            
            with st.spinner("Agent is analyzing logs (this may take a minute locally)..."):
                # Changed timeout to None so the local LLM has enough time to finish running its tools
                response = requests.post(API_URL, json=payload, timeout=None)
            
            if response.status_code == 200:
                agent_answer = response.json().get("answer", "No answer received.")
                response_placeholder.markdown(agent_answer)
                # Save assistant response to history
                st.session_state.messages.append({"role": "assistant", "content": agent_answer})
            else:
                error_msg = f"❌ API Error ({response.status_code}): {response.text}"
                response_placeholder.error(error_msg)
                
        except requests.exceptions.Timeout:
            response_placeholder.error("❌ Request Timed Out. The local AI took too long to generate tokens. Please try again.")
        except requests.exceptions.ConnectionError:
            response_placeholder.error("❌ Connection Failed. Make sure your FastAPI backend server is running on port 8000!")

