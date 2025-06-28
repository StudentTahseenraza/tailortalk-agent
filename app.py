import streamlit as st
import requests

def main():
    st.set_page_config(page_title="TailorTalk - Appointment Booking", page_icon="📅", layout="centered")
    st.title("TailorTalk - Appointment Booking Agent")
    st.markdown("Hi! I'm TailorTalk, your friendly assistant for scheduling appointments. Just tell me when you'd like to book a meeting, and I'll handle the rest!")

    API_URL = "https://tailortalk-agent-1.onrender.com"  # ✅ Use deployed backend

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("What would you like to do? (e.g., 'Schedule a call tomorrow afternoon')"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        try:
            response = requests.post(f"{BACKEND_URL}/chat", json={"input": prompt})
            response.raise_for_status()
            assistant_response = response.json().get("response", "Sorry, something went wrong.")
        except requests.RequestException as e:
            assistant_response = f"Sorry, I couldn't connect to the server. Please try again.\n\nError: {str(e)}"

        st.session_state.messages.append({"role": "assistant", "content": assistant_response})
        with st.chat_message("assistant"):
            st.markdown(assistant_response)

if __name__ == "__main__":
    main()
