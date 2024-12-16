import streamlit as st
from streamlit_extras.colored_header import colored_header
import streamlit_antd_components as sac
import uuid
import requests
import os

st.set_page_config(
    page_title="Interview Coach",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Clear session state on page load
if not st.session_state.get('initialized'):
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.session_state.initialized = True

USER_ID = str(uuid.uuid4())
RASA_BASE_URL = os.environ.get("RASA_BASE_URL", "http://localhost:5005")
WEBHOOK_URL = "/webhooks/rest/webhook"

def user_icon():
    return "🧑‍💼"

def assistant_icon():
    return "👨‍🏫"

def reset_conversation():
    # Send restart command to Rasa
    requests.post(f"{RASA_BASE_URL}{WEBHOOK_URL}", json={"sender_id": USER_ID, "message": "restart"})
    
    # Reset chat messages
    st.session_state.messages = [{
        "role": "assistant", 
        "content": "👋 Welcome! I'm your personal interview coach. I can help you:\n"
                  "• Prepare for common interview questions\n"
                  "• Practice with mock interviews\n"
                  "• Learn about interview etiquette\n"
                  "• Get feedback on your responses\n\n"
                  "What would you like to work on today?"
    }]

def send_message_to_rasa(prompt):
    with st.status("Processing...", expanded=False):
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.chat_message("user", avatar=user_icon()).write(prompt)
        response = requests.post(f"{RASA_BASE_URL}{WEBHOOK_URL}", json={"sender_id": USER_ID, "message": prompt}).json()
        try:
            for msg in response:
                if "text" in msg:
                    text = msg["text"]
                    st.session_state.messages.append({"role": "assistant", "content": text})
                    st.chat_message("assistant", avatar=assistant_icon()).write(text.replace("\n", "  \n"))
                elif "image" in msg:
                    image_url = msg["image"]
                    st.session_state.messages.append({"role": "assistant", "content": f"![image]({image_url})"})
                    st.chat_message("assistant", avatar=assistant_icon()).write(f"![image]({image_url})")
        except KeyError:
            pass
    st.rerun()

colored_header(
    label="💬 Interview Coach",
    description="📈 Your AI companion for interview preparation and practice",
    color_name="violet-70"
)

with st.sidebar:
    sac.divider(label='Your Profile', icon='person-circle', align='center')
    user = st.text_input("User ID", key="id", type="default", value=USER_ID, disabled=True)
    st.button("Reset Conversation", on_click=reset_conversation, type="primary")
    
    sac.divider(label='Quick Commands', icon='chat-dots', align='center')

    example_prompts = [
        ("🔄 Restart", "restart"),
        ("❓ Help", "help"),
        ("📝 How to prepare?", "How to prepare?"),
        ("💭 Example interview questions", "Example interview questions"),
        ("🎯 Mock interview question", "Mock interview question"),
        ("📋 Summarize my mock interview", "Summarize my mock interview"),
        ("🤖 Let AI review my mock interview", "Let AI review my mock interview"),
        ("👔 What should I wear?", "What should I wear?"),
        ("👚 What does business casual look like?", "What does business casual look like?"),
        ("💻 Provide an easy sorting leetcode question", "Provide an easy sorting leetcode question")
    ]

    for label, prompt in example_prompts:
        if st.sidebar.button(label, use_container_width=True):
            if prompt.lower().strip() == "restart":
                reset_conversation()
                st.rerun()
            else:
                send_message_to_rasa(prompt)
    
    sac.divider(label='Resources', icon='book', align='center')
    sac.buttons([
        sac.ButtonsItem(label='Source Code', icon='github', href='https://github.com/NicoDoebele/job-interview-chatbot')
    ], format_func='title', align='left')

if "messages" not in st.session_state or "reset" in st.query_params:
    reset_conversation()

for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.chat_message(msg["role"], avatar=user_icon()).write(msg["content"].replace("\n", "  \n"))
    else:
        st.chat_message(msg["role"], avatar=assistant_icon()).write(msg["content"].replace("\n", "  \n"))

# Add buttons after messages
col1, col2, col3, col4, _ = st.columns([1, 1, 0.8, 0.8, 0.4])
with col1:
    if st.button("📝 Example Questions", use_container_width=True):
        send_message_to_rasa("Provide some example interview questions")

with col2:
    if st.button("🎯 Mock Interview Question", use_container_width=True):
        send_message_to_rasa("Provide a mock interview question")

with col3:
    if st.button("🤖 AI Mock Interview Review", use_container_width=True):
        send_message_to_rasa("Let AI review my mock interview")

with col4:
    if st.button("📋 Mock interview summary", use_container_width=True):
        send_message_to_rasa("Summarize my mock interview")

# Then the chat input
if prompt := st.chat_input():
    if prompt.lower().strip() == "restart":
        reset_conversation()
        st.rerun()
    else:
        send_message_to_rasa(prompt)