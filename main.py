import os
import streamlit as st
from dotenv import load_dotenv
from google import genai
from google.genai import types

# 1. Setup & Security
load_dotenv()
# The new SDK automatically looks for GEMINI_API_KEY or GOOGLE_API_KEY
api_key = os.getenv("GOOGLE_API_KEY")

st.set_page_config(page_title="Chat with Dude!", page_icon="🧠", layout="centered")

# 2. Initialize the Modern Client
if not api_key:
    st.error("Missing API Key. Please set GOOGLE_API_KEY in your .env file.")
    st.stop()

# Creating the global client
client = genai.Client(api_key=api_key)
MODEL_ID = "models/gemini-3-flash-preview"  # The latest high-speed model

# 3. Session State Management
# In the new SDK, we store the 'history' in state, not the model object
if "messages" not in st.session_state:
    st.session_state.messages = []

st.title("🤖 Dude - ChatBot")

# 4. Display Chat History
# The new SDK uses a 'role' and 'content' structure
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 5. Chat Input & Logic
if prompt := st.chat_input("Ask Dude..."):
    # Display user message
    st.chat_message("user").markdown(prompt)

    # Store user message in history
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Call the API using the modern 'models.generate_content' method
    try:
        # We pass the whole history to maintain context
        response = client.models.generate_content(
            model=MODEL_ID,
            contents=[
                types.Content(role=m["role"], parts=[types.Part(text=m["content"])])
                for m in st.session_state.messages
            ]
        )

        ai_response = response.text

        # Display and save assistant response
        with st.chat_message("assistant"):
            st.markdown(ai_response)

        st.session_state.messages.append({"role": "assistant", "content": ai_response})

    except Exception as e:
        st.error(f"AI Error: {e}")

if st.sidebar.button("List Available Models"):
    models = client.models.list()
    for m in models:
        st.sidebar.write(m.name)