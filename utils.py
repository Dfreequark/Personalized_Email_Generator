import os
import streamlit as st
from streamlit.logger import get_logger
from langchain_cohere import ChatCohere


logger = get_logger('Langchain-Chatbot')



os.environ["LANGCHAIN_API_KEY"]= st.secrets["LANGCHAIN_API_KEY"]
os.environ["LANGCHAIN_TRACING_V2"]="false"

#decorator
def enable_chat_history(func):
    # if os.environ.get("OPENAI_API_KEY"):
    if os.environ["COHERE_API_KEY"]:

        # to clear chat history after swtching chatbot
        current_page = func.__qualname__
        if "current_page" not in st.session_state:
            st.session_state["current_page"] = current_page
        if st.session_state["current_page"] != current_page:
            try:
                st.cache_resource.clear()
                del st.session_state["current_page"]
                del st.session_state["messages"]
            except:
                pass

        # # to show chat history on ui
        if "messages" not in st.session_state:
            st.session_state["messages"]= []
            # st.session_state["messages"] = [ChatMessage(role="assistant", content="How can I assist you to improve your vocabulary?")]
            # st.session_state["messages"] = [{"role": "assistant", "content": "How can I assist you?"}]
            # st.chat_message("assistant").write("How can I assist you to improve your vocabulary?")

       
        for msg in st.session_state["messages"]:
            st.chat_message(msg["role"]).write(msg["content"])

    def execute(*args, **kwargs):
        func(*args, **kwargs)
    return execute

def clear_chat_history():
    """Clears chat history, useful when switching between chatbots."""
    if "messages" in st.session_state:
        del st.session_state["messages"]



def display_msg(msg, author):
    st.session_state.messages.append({"role": author, "content": msg})
    st.chat_message(author).write(msg)

def user_api_key():
    cohere_api_key = st.sidebar.text_input(
        label="Enter Your Cohere API Key",
        type="password",
        placeholder="api key...",
        key="SELECTED_COHERE_API_KEY"
        )
    if not cohere_api_key:
        st.error("Please add your Cohere API key to continue.")
        st.info("Obtain your key from this link: https://cohere.com/")
        st.stop()

    return cohere_api_key


def configure_llm():
    llm = ChatCohere(model="command-r-plus", streaming=True)
    return llm

def sync_st_session():
    for k, v in st.session_state.items():
        st.session_state[k] = v