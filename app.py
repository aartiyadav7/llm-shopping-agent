import streamlit as st
import json
from pathlib import Path

# Page configuration
st.set_page_config(
    page_title="AI Shopping Agent",
    page_icon="🛍️",
    layout="wide",
    initial_sidebar_state="expanded"
)

from utils.database import db

# Initialize session state from Database
user_id = st.session_state.get('user_id', "guest_001")
user_data = db.get_user(user_id)

if 'user_id' not in st.session_state:
    st.session_state.user_id = user_id
if 'user_preferences' not in st.session_state:
    st.session_state.user_preferences = user_data.get('preferences', {})
if 'cart' not in st.session_state:
    st.session_state.cart = db.get_cart(user_id)
if 'browsing_history' not in st.session_state:
    st.session_state.browsing_history = [h['product_id'] for h in db.get_browsing_history(user_id)]
if 'wishlist' not in st.session_state:
    st.session_state.wishlist = db.get_wishlist(user_id)

# Custom CSS for modern premium theme
st.markdown("""
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&display=swap" rel="stylesheet">
    <style>
    /* Global Styles */
    html, body, [class*="st-"] {
        font-family: 'Outfit', sans-serif;
    }

    .main {
        background-color: #f8faff;
    }

    /* Glassmorphism Header */
    .hero-section {
        background: linear-gradient(135deg, rgba(26, 115, 232, 0.9), rgba(102, 126, 234, 0.9));
        padding: 4rem 2rem;
        border-radius: 24px;
        color: white;
        text-align: center;
        margin-bottom: 3rem;
        box-shadow: 0 20px 40px rgba(26, 115, 232, 0.2);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.2);
    }

    .main-header {
        font-size: 4.5rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
        letter-spacing: -2px;
        background: linear-gradient(to right, #ffffff, #e0e0e0);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    .sub-header {
        font-size: 1.5rem;
        opacity: 0.9;
        font-weight: 300;
        margin-bottom: 2rem;
    }

    /* Premium Feature Cards */
    .feature-card {
        background: white;
        padding: 2.5rem;
        border-radius: 20px;
        border: 1px solid #eef2f6;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.05);
        text-align: center;
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        height: 100%;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
    }

    .feature-card:hover {
        transform: translateY(-12px);
        box-shadow: 0 20px 40px rgba(26, 115, 232, 0.1);
        border-color: #1A73E8;
    }

    .feature-icon {
        font-size: 3.5rem;
        margin-bottom: 1.5rem;
        background: #f0f7ff;
        width: 80px;
        height: 80px;
        display: flex;
        align-items: center;
        justify-content: center;
        border-radius: 20px;
    }

    .feature-card h3 {
        color: #1a202c;
        font-weight: 600;
        margin-bottom: 1rem;
        font-size: 1.4rem;
    }

    .feature-card p {
        color: #4a5568;
        font-size: 1rem;
        line-height: 1.6;
    }

    /* Modern Metrics */
    .metric-container {
        display: flex;
        justify-content: space-between;
        gap: 1.5rem;
        margin: 3rem 0;
    }

    .metric-card {
        background: rgba(255, 255, 255, 0.8);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(26, 115, 232, 0.1);
        padding: 1.5rem;
        border-radius: 18px;
        flex: 1;
        text-align: center;
        transition: transform 0.3s;
    }

    .metric-card:hover {
        transform: scale(1.05);
        background: white;
    }

    .metric-value {
        font-size: 2rem;
        font-weight: 700;
        color: #1A73E8;
        display: block;
    }

    .metric-label {
        font-size: 0.9rem;
        color: #718096;
        text-transform: uppercase;
        letter-spacing: 1px;
    }

    /* Utility Boxes */
    .stInfo, .stSuccess {
        border-radius: 15px !important;
        border: none !important;
        padding: 1.2rem !important;
    }
    
    .stInfo { background-color: #eef6ff !important; color: #1a73e8 !important; }
    .stSuccess { background-color: #f0fff4 !important; color: #2f855a !important; }

    /* Button Styling */
    .stButton>button {
        border-radius: 12px !important;
        padding: 0.6rem 2rem !important;
        font-weight: 600 !important;
        transition: all 0.3s !important;
    }
    </style>
""", unsafe_allow_html=True)

# ------------------------------------------
# 🏠 Hero Section
# ------------------------------------------
st.markdown("""
    <div class="hero-section">
        <h1 class="main-header">Shop with Intelligence</h1>
        <p class="sub-header">Experience the next generation of e-commerce, powered by advanced AI and real-time comparisons.</p>
        <div style="display: flex; justify-content: center; gap: 1rem; margin-top: 2rem;">
            <a href="home" target="_self" style="background: white; color: #1A73E8; padding: 0.8rem 2.5rem; border-radius: 12px; font-weight: 600; text-decoration: none; box-shadow: 0 10px 20px rgba(0,0,0,0.1);">Enter Store</a>
            <a href="chat_assistant" target="_self" style="background: rgba(255,255,255,0.1); color: white; padding: 0.8rem 2.5rem; border-radius: 12px; font-weight: 600; border: 1px solid rgba(255,255,255,0.4); text-decoration: none; backdrop-filter: blur(5px);">Chat with AI</a>
        </div>
    </div>
""", unsafe_allow_html=True)

# ------------------------------------------
# 📊 Metrics Dashboard
# ------------------------------------------
st.markdown("""
    <div class="metric-container">
        <div class="metric-card">
            <span class="metric-value">150+</span>
            <span class="metric-label">Curated Products</span>
        </div>
        <div class="metric-card">
            <span class="metric-value">Real-time</span>
            <span class="metric-label">Price Logic</span>
        </div>
        <div class="metric-card">
            <span class="metric-value">94%</span>
            <span class="metric-label">AI Accuracy</span>
        </div>
    </div>
""", unsafe_allow_html=True)

# ------------------------------------------
# ✨ Core Capabilities
# ------------------------------------------
st.markdown("<h2 style='text-align: center; margin-bottom: 3rem; color: #1a202c; font-weight: 700; font-size: 2.5rem;'>The Future of Shopping</h2>", unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">🔍</div>
            <h3>Semantic Search</h3>
            <p>Our AI understands intent, not just keywords. Find the perfect match for 'cozy', 'professional', or 'adventure'.</p>
        </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">💰</div>
            <h3>Price Comparison</h3>
            <p>Real-time fetching from Amazon, eBay, and more. Always find the absolute lowest price for every item.</p>
        </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">🤖</div>
            <h3>Agentic Assistant</h3>
            <p>A personal shopper that can manage your cart, apply discounts, and provide expert styling advice 24/7.</p>
        </div>
    """, unsafe_allow_html=True)

st.markdown("<br><br>", unsafe_allow_html=True)

# Getting started section
st.markdown("---")
st.subheader("🚀 Quick Navigation")

col1, col2, col3 = st.columns(3)

with col1:
    st.info("👈 **Check the Sidebar** to switch between modules like Browse, Chat, and Profile.", icon="ℹ️")

with col2:
    st.success("✨ **Personalized Flow**: Add items to your cart, and the AI will automatically adapt.", icon="✅")

with col3:
    if st.button("Start Shopping Now", use_container_width=True, type="primary"):
        st.switch_page("pages/1_home.py")

# Footer
st.markdown("<br>", unsafe_allow_html=True)
st.markdown("""
    <div style="text-align: center; padding: 2rem; color: #718096; border-top: 1px solid #eef2f6;">
        <p>© 2024 AI Shopping Agent | Advanced E-commerce Intelligence</p>
        <p style="font-size: 0.8rem;">Powered by OpenAI & Premium Design Patterns</p>
    </div>
""", unsafe_allow_html=True)