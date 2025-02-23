import streamlit as st
import requests
import uuid

API_URL = "http://localhost:3000/api/v1/prediction/84adcd72-17ed-40a3-bf25-59c9213563f1"

def query(payload):
    """Send text input to the backend."""
    response = requests.post(API_URL, json=payload)
    return response.json()

st.title("Study Assistant App")

# Initialize session state variables
if 'messages' not in st.session_state:
    st.session_state['messages'] = []
if 'chat_id' not in st.session_state:
    st.session_state['chat_id'] = str(uuid.uuid4())
if 'session_id' not in st.session_state:
    st.session_state['session_id'] = str(uuid.uuid4())
if 'chat_message_id' not in st.session_state:
    st.session_state['chat_message_id'] = None  

# Display chat history
for message in st.session_state['messages']:
    role = message['role'].lower()
    with st.chat_message(role):
        st.write(message['content'])

# Accept user input
user_input = st.chat_input("Type your message here...")

if user_input:
    st.session_state['chat_message_id'] = str(uuid.uuid4())

    # Append user message
    st.session_state['messages'].append({'role': 'user', 'content': user_input})
    with st.chat_message("user"):
        st.write(user_input)

    # Prepare and send request
    payload = {
        "question": user_input,
        "chatId": st.session_state['chat_id'],
        "sessionId": st.session_state['session_id'],
        "chatMessageId": st.session_state['chat_message_id'],
    }
    
    try:
        data = query(payload)
        bot_reply = data.get('text', 'No response from the bot.')
        
        # Append bot response
        st.session_state['messages'].append({'role': 'assistant', 'content': bot_reply})
        with st.chat_message("assistant"):
            st.write(bot_reply)
    
    except requests.exceptions.RequestException as e:
        st.error(f"An error occurred: {e}")

# File Upload Section (Hidden until clicked)
with st.expander("📁 Upload a Lesson Note"):
    uploaded_file = st.file_uploader("Choose a file", type=["txt"])

    if uploaded_file:
        st.session_state['chat_message_id'] = str(uuid.uuid4())

        # Read file content
        file_content = uploaded_file.read().decode("utf-8")
        file_prompt = f"Create a lesson revision plan based on this lesson note:\n{file_content}"

        # Append user file upload message
        st.session_state['messages'].append({'role': 'user', 'content': f"📄 Uploaded file: {uploaded_file.name}"})
        with st.chat_message("user"):
            st.write(f"📄 Uploaded file: {uploaded_file.name}")

        # Prepare and send request
        payload = {
            "question": file_prompt,
            "chatId": st.session_state['chat_id'],
            "sessionId": st.session_state['session_id'],
            "chatMessageId": st.session_state['chat_message_id'],
        }

        try:
            data = query(payload)
            bot_reply = data.get('text', 'No response from the bot.')

            # Append bot response
            st.session_state['messages'].append({'role': 'assistant', 'content': bot_reply})
            with st.chat_message("assistant"):
                st.write(bot_reply)

        except requests.exceptions.RequestException as e:
            st.error(f"File processing failed: {e}")
