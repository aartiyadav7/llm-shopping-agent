from utils.database import db
from models.recommender import recommender
import streamlit as st
import json
from pathlib import Path
import random
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

st.set_page_config(page_title="Chat Assistant", page_icon="💬", layout="wide")

# Custom CSS for Premium Chat UI
st.markdown("""
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&display=swap" rel="stylesheet">
    <style>
    html, body, [class*="st-"] {
        font-family: 'Outfit', sans-serif;
    }
    
    .stChatMessage {
        background-color: white !important;
        border-radius: 15px !important;
        padding: 1.5rem !important;
        margin-bottom: 1rem !important;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05) !important;
        border: 1px solid #f0f2f6 !important;
    }
    
    .stChatMessage[data-testimonial="user"] {
        background-color: #f0f7ff !important;
        border-color: #e0eaff !important;
    }

    .main {
        background-color: #f8faff;
    }

    h1 {
        font-weight: 700 !important;
        color: #1A73E8 !important;
        letter-spacing: -1px !important;
    }
    
    .stChatInputContainer {
        border-radius: 20px !important;
        background: white !important;
        box-shadow: 0 -10px 30px rgba(0,0,0,0.05) !important;
    }
    </style>
""", unsafe_allow_html=True)

# Load products
@st.cache_data
def load_products():
    products_file = Path("data/products.json")
    if products_file.exists():
        with open(products_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

products = load_products()

# Initialize chat history
if 'messages' not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "👋 Hi! I'm your AI shopping assistant. How can I help you today?"}
    ]

from models.agent_tools import TOOLS, AVAILABLE_FUNCTIONS

def get_ai_response_fallback(user_message):
    """Simple rule-based fallback if OpenAI is unreachable"""
    message_lower = user_message.lower()
    if any(word in message_lower for word in ['hi', 'hello', 'hey']):
        return "Hello! 😊 I'm currently in basic mode, but I can still help you find products!"
    
    # Use the hybrid recommender's fallback (which uses keyword matching)
    results = recommender.get_hybrid_recommendations(user_message, n=2)
    if results:
        response = f"I found some items you might like:\n\n"
        for p in results:
            response += f"• **{p['name']}** (${p['price']}) - {p['image']}\n"
        return response
    
    return "I'm sorry, I'm having trouble reach my AI brain right now, but feel free to browse our products! 🛍️"

def get_ai_response(user_message):
    """Generate AI response using OpenAI Tool Calling (ReAct Agent Pattern)"""
    
    if not os.getenv("OPENAI_API_KEY"):
        return get_ai_response_fallback(user_message)

    try:
        # Build the system prompt
        system_prompt = """
        You are a highly capable, autonomous AI Shopping Assistant.
        You have access to tools to search the catalog, get product details, check the user's cart, and view their preferences.
        Use these tools iteratively to answer the user's question, find the best products, or help them with their shopping experience.
        Be enthusiastic, concise, and format your final response nicely using markdown (bullet points, bold text).
        If you recommend a product, always mention its price and a brief reason why.
        """

        # Prepare messages including history
        messages = [{"role": "system", "content": system_prompt}]
        
        # Add last 6 messages from history for context (skip the first greeting)
        history = st.session_state.messages[1:] if len(st.session_state.messages) > 1 else []
        for msg in history[-6:]:
            # Make sure we only add standard messages, not function call logs from previous turns to keep it simple
            if msg["role"] in ["user", "assistant"] and isinstance(msg["content"], str):
                 messages.append({"role": msg["role"], "content": msg["content"]})
                 
        messages.append({"role": "user", "content": user_message})

        # Step 1: Send the conversation and tools to the model
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            tools=TOOLS,
            tool_choice="auto",
            timeout=15.0
        )
        
        response_message = response.choices[0].message
        tool_calls = response_message.tool_calls

        # Step 2: Check if the model wanted to call a function
        if tool_calls:
            messages.append(response_message)  # Extend conversation with assistant's reply
            
            # Step 3: Call the function
            for tool_call in tool_calls:
                function_name = tool_call.function.name
                function_to_call = AVAILABLE_FUNCTIONS.get(function_name)
                
                if function_to_call:
                    try:
                        function_args = json.loads(tool_call.function.arguments)
                        function_response = function_to_call(**function_args)
                    except Exception as e:
                        function_response = f"Error executing tool: {e}"
                else:
                    function_response = f"Tool '{function_name}' not found."
                
                # Step 4: Send the info back to the model
                messages.append(
                    {
                        "tool_call_id": tool_call.id,
                        "role": "tool",
                        "name": function_name,
                        "content": str(function_response),
                    }
                )
            
            # Get the final response from the model
            second_response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages,
                timeout=15.0
            )
            return second_response.choices[0].message.content

        return response_message.content

    except Exception as e:
        print(f"OpenAI error: {e}")
        return get_ai_response_fallback(user_message)

# Page header
st.title("💬 AI Shopping Assistant")
st.markdown("Ask me anything about products, get recommendations, or compare items!")

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Type your message here..."):
    # Add user message to chat
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Generate AI response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = get_ai_response(prompt)
            st.markdown(response)
    
    # Add assistant response to chat
    st.session_state.messages.append({"role": "assistant", "content": response})

# Sidebar - Quick Actions
st.sidebar.header("💡 Quick Actions")

if st.sidebar.button("🎁 Show Today's Deals"):
    st.session_state.messages.append({
        "role": "assistant", 
        "content": "🎉 Today's Special Deals:\n\n• 20% off Electronics\n• Buy 2 Get 1 Free Skincare\n• Free Shipping over $50"
    })
    st.rerun()

if st.sidebar.button("👔 Suggest an Outfit"):
    # Use hybrid recommender for outfit
    clothing_products = recommender.get_hybrid_recommendations("stylish outfit", n=3)
    response = "I've curated a stylish outfit for you! 👔\n\n"
    for p in clothing_products:
        response += f"• {p['name']} - ${p['price']}\n"
    st.session_state.messages.append({"role": "assistant", "content": response})
    st.rerun()

if st.sidebar.button("🧴 Skincare Routine"):
    skincare_products = recommender.get_hybrid_recommendations("skincare routine", n=3)
    response = "Your personalized skincare routine:\n\n"
    for p in skincare_products:
        response += f"• {p['name']} - ${p['price']}\n"
    st.session_state.messages.append({"role": "assistant", "content": response})
    st.rerun()

if st.sidebar.button("🔄 Clear Chat"):
    st.session_state.messages = [
        {"role": "assistant", "content": "Chat cleared! How can I help you?"}
    ]
    st.rerun()

# Cart summary in sidebar
st.sidebar.markdown("---")
st.sidebar.subheader("🛒 Your Cart")
if 'cart' in st.session_state and len(st.session_state.cart) > 0:
    cart_total = sum([item['price'] for item in st.session_state.cart])
    st.sidebar.success(f"**{len(st.session_state.cart)} items** - ${cart_total:.2f}")
else:
    st.sidebar.info("Cart is empty")
