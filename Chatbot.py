import streamlit as st
import uuid
import requests

USER_ID = str(uuid.uuid4())
RASA_BASE_URL = "http://localhost:5005"
WEBHOOK_URL = "/webhooks/rest/webhook"

with st.sidebar:
    user = st.text_input("User ID", key="id", type="default", value=USER_ID, disabled=True)
    "[View the source code](https://github.com/NicoDoebele/job-interview-chatbot)"
    "[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/NicoDoebele/job-interview-chatbot?quickstart=1)"

st.title("💬 Job Interview Chatbot")
st.caption("🎓 A Rasa + Streamlit chatbot developed for NLP")
if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content": "Hello! What questions do you have about your upcoming interviews? I can assist you with your interview preparation, provide common questions, explain expected behavior and more. Just ask your questions or request a short mock interview!"}]

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"].replace("\n", "  \n"))

if prompt := st.chat_input():
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    # get response from local rasa chatbot via http
    response = requests.post(f"{RASA_BASE_URL}{WEBHOOK_URL}", json={"sender_id": USER_ID, "message": prompt}).json()
    messages = [msg["text"] for msg in response]
    for msg in messages:
        st.session_state.messages.append({"role": "assistant", "content": msg})
        st.chat_message("assistant").write(msg.replace("\n", "  \n"))