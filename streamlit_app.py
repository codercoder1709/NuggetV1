import streamlit as st
from src.chatbot.chatbot import chatbot_respond # Assuming chatbot.py is in the src folder

st.set_page_config(page_title="Restaurant Chatbot 🍴", page_icon="🍔", layout="centered")

st.title("🍽️ Restaurant Chatbot")
st.caption("Ask me anything about available dishes, restaurants, locations...") # Using caption for subheader style

# Initialize session state for chat history if it doesn't exist
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Hi! How can I help you find something delicious today?"}]

# Display chat history on each rerun
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"]) # Use markdown for better formatting potential

# Chat input at the bottom
user_input = st.chat_input("Type your question here...")

if user_input:
    # Add user message to chat history and display it
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # Get bot response
    # Display a thinking indicator while processing
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            bot_response = chatbot_respond(user_input)
            st.markdown(bot_response) # Display bot response

    # Add bot response to chat history
    st.session_state.messages.append({"role": "assistant", "content": bot_response})

# Optional: Add a button to clear chat history
# if st.button("Clear Chat"):
#     st.session_state.messages = [{"role": "assistant", "content": "Hi! How can I help you find something delicious today?"}]
#     st.rerun()