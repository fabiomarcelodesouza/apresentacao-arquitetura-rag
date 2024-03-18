import os
import warnings
import sys
import streamlit as st
from rag import ask_rag

warnings.filterwarnings("ignore")

# Get the directory of the current file
current_dir = os.path.dirname(os.path.abspath(__file__))
empresa = "Mobilize Financial Services"

# Define the path relative to the current file
# For example, if the directory to add is the parent directory of the current file
parent_dir = os.path.join(current_dir, "..")

# Add the parent directory to sys.path
sys.path.insert(0, parent_dir)

st.set_page_config(page_title="Exemplo de arquitetura RAG - Mobilize Financial Services")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

st.title(f"Exemplo de arquitetura RAG - {empresa}")

def reset_conversation():
    st.session_state.messages = []

col1, col2 = st.columns([3, 1])
with col2:
    st.button("Reset Chat", on_click=reset_conversation)

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        if message["role"] == "assistant":            
            st.markdown(message["content"])
        else:
            st.markdown(message["content"])


# Accept user input
if prompt := st.chat_input("Em que posso ajudar:"):
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    response, source = ask_rag(prompt, empresa)
    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        #display_text_with_images(response)        
        st.markdown(response)

        texto = "Fontes dos documentos consultados:"
        html = f"<span style='font-size: 12px;'>{texto}</span>"
    
        st.markdown(html, unsafe_allow_html=True)
        
        for fonte in source:
            texto = f"Documento: {fonte['source']} - Página: {fonte['page']}"
            html = f"<span style='font-size: 12px;'>{texto}</span>"

            st.markdown(html, unsafe_allow_html=True)

    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": response})

