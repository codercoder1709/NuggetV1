import streamlit as st
from src.chatbot.chatbot import chatbot_respond

# Page configuration with custom theme
st.set_page_config(
    page_title="SwiggyBot - Your Food Concierge 🍽️",
    page_icon="🍴",
    layout="wide"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .stApp {
        background-color: #f5f5f5;
    }
    .chat-container {
        background-color: white;
        border-radius: 10px;
        padding: 20px;
        margin: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .user-message {
        background-color: #FF5722;
        color: white;
        padding: 10px;
        border-radius: 15px;
        margin: 5px;
    }
    .bot-message {
        background-color: #f0f0f0;
        padding: 10px;
        border-radius: 15px;
        margin: 5px;
    }
    </style>
""", unsafe_allow_html=True)

# App header with Swiggy-like branding
col1, col2, col3 = st.columns([1,2,1])
with col2:
    st.image("https://images.pexels.com/photos/1640774/pexels-photo-1640774.jpeg", width=200)
    st.title("SwiggyBot - Your Personal Food Concierge")
    st.caption("Ask me anything about restaurants, dishes, or dietary preferences!")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": "👋 Hi! I'm SwiggyBot, your personal food concierge. How can I help you find something delicious today?"
        }
    ]

# Chat container
st.markdown('<div class="chat-container">', unsafe_allow_html=True)

# Display chat history
for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.markdown(f'<div class="user-message">{msg["content"]}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="bot-message">{msg["content"]}</div>', unsafe_allow_html=True)

# Chat input
user_input = st.chat_input("What food are you craving today? 😋")

if user_input:
    # Add user message
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    # Get bot response
    with st.spinner("SwiggyBot is thinking... 🤔"):
        bot_response = chatbot_respond(user_input)
        st.session_state.messages.append({"role": "assistant", "content": bot_response})
    
    # Force rerun to update chat
    st.rerun()

# Quick filters
st.sidebar.title("Quick Filters")
st.sidebar.markdown("### Dietary Preferences")
st.sidebar.checkbox("Vegetarian")
st.sidebar.checkbox("Vegan")
st.sidebar.checkbox("Gluten-Free")

st.sidebar.markdown("### Price Range")
price_range = st.sidebar.slider("Maximum Price (₹)", 0, 1000, 500)

st.sidebar.markdown("### Sort By")
st.sidebar.radio("", ["Rating", "Price: Low to High", "Price: High to Low", "Delivery Time"])

# Popular searches
st.sidebar.markdown("### Popular Searches")
st.sidebar.button("🔥 Spicy Biryani")
st.sidebar.button("🍕 Pizza Deals")
st.sidebar.button("🥗 Healthy Options")