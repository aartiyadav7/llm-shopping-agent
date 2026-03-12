import streamlit as st
import sys
from pathlib import Path

# Add parent directory to path to import models
sys.path.append(str(Path(__file__).parent.parent))
from models.recommender import recommender

# Streamlit page configuration
st.set_page_config(page_title="Home", page_icon="🏠", layout="wide")
from utils.database import db

# Custom CSS for Premium UI
st.markdown("""
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&display=swap" rel="stylesheet">
    <style>
    html, body, [class*="st-"] {
        font-family: 'Outfit', sans-serif;
    }
    
    .main {
        background-color: #f8faff;
    }

    h1, h2, h3 {
        font-weight: 700 !important;
        color: #1A73E8 !important;
        letter-spacing: -1px !important;
    }

    .hero-banner {
        background: linear-gradient(135deg, #1A73E8, #667eea);
        padding: 4rem 2rem;
        border-radius: 24px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 15px 35px rgba(26, 115, 232, 0.2);
    }

    .premium-card {
        background: white;
        padding: 1.5rem;
        border-radius: 20px;
        border: 1px solid #eef2f6;
        box-shadow: 0 10px 25px rgba(0, 0, 0, 0.03);
        transition: transform 0.3s ease;
    }

    .premium-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 35px rgba(26, 115, 232, 0.08);
    }
    </style>
""", unsafe_allow_html=True)

# ------------------------------------------
# 🏠 Header Section
# ------------------------------------------
st.markdown("""
<div class="hero-banner">
    <h1 style="color: white !important; font-size: 3.5rem; margin-bottom: 0.5rem;">AI-Driven Shopping</h1>
    <p style="font-size: 1.3rem; opacity: 0.9;">Predictive Recommendations • Visual Search • Price Intel</p>
</div>
""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ------------------------------------------
# ⚡ Quick Action Nav
# ------------------------------------------
col1, col2, col3, col4 = st.columns(4)

with col1:
    if st.button("🛍️ Catalog", key="browse_products", use_container_width=True):
        st.switch_page("pages/2_browse_products.py")

with col2:
    if st.button("💬 Assistant", key="chat_ai", use_container_width=True, type="primary"):
        st.switch_page("pages/3_chat_assistant.py")

with col3:
    if st.button("🛒 Your Cart", key="view_cart", use_container_width=True):
        st.switch_page("pages/4_shopping_cart.py")

with col4:
    if st.button("👤 Profile", key="my_profile", use_container_width=True):
        st.switch_page("pages/5_profile.py")

st.markdown("---")

# ------------------------------------------
# ✨ Personalized Recommendations
# ------------------------------------------
st.subheader("✨ Recommended Just For You")

user_prefs = st.session_state.get('user_preferences', {})
browsing_history = st.session_state.get('browsing_history', [])

recommendations = recommender.get_personalized_recommendations(
    user_prefs,
    browsing_history,
    n=6
)

cols = st.columns(3)
for idx, product in enumerate(recommendations):
    with cols[idx % 3]:
        st.markdown(f"""
        <div class="premium-card">
            <div style="font-size: 3rem; text-align: center; margin-bottom: 1rem;">{product['image']}</div>
            <h4 style="margin: 0;">{product['name']}</h4>
            <p style="color: #718096; font-size: 0.9rem;">{product['category']} • ⭐ {product['rating']}</p>
            <h3 style="margin-top: 0.5rem;">${product['price']:.2f}</h3>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("Add to Cart", key=f"add_{product['id']}", use_container_width=True):
            if 'cart' not in st.session_state:
                st.session_state.cart = []
            st.session_state.cart.append(product)
            # Sync to DB
            db.update_cart(st.session_state.user_id, st.session_state.cart)
            st.success(f"Added {product['name']} to cart!")
            st.rerun()
        st.markdown("<br>", unsafe_allow_html=True)

st.markdown("---")

# ------------------------------------------
# 🔥 Trending Products
# ------------------------------------------
st.subheader("🔥 Trending Now")

trending = recommender.get_trending_products(n=4)

cols = st.columns(4)
for idx, product in enumerate(trending):
    with cols[idx]:
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
                    padding: 0.5rem; border-radius: 10px; text-align: center; color: white;">
            <div style="font-size: 2.5rem;">{product['image']}</div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown(f"**{product['name']}**")
        st.caption(f"${product['price']} • ⭐ {product['rating']}")

st.markdown("---")

# ------------------------------------------
# 🗂️ Shop by Category
# ------------------------------------------
st.subheader("🗂️ Shop by Category")

categories = [
    ("Electronics", "💻", "#667eea"),
    ("Clothing", "👕", "#f59f00"),
    ("Skincare", "🧴", "#51cf66"),
    ("Sports", "⚽", "#ff6b6b")
]

cols = st.columns(4)
for idx, (category, emoji, color) in enumerate(categories):
    with cols[idx]:
        st.markdown(f"""
        <div style="background-color: {color}; padding: 2rem; border-radius: 10px;
                    text-align: center; color: white; cursor: pointer;">
            <div style="font-size: 3rem;">{emoji}</div>
            <h4>{category}</h4>
        </div>
        """, unsafe_allow_html=True)

st.markdown("---")

# ------------------------------------------
# 🎁 Special Offers
# ------------------------------------------
st.subheader("🎁 Special Offers")

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    <div style="background-color: #f59f00; color: white; padding: 1.5rem; 
                border-radius: 12px; text-align: center;">
        <h3>🎉 Flash Sale!</h3>
        <p><strong>20% OFF</strong> on all Electronics</p>
        <p><em>Valid until midnight</em></p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div style="background-color: #51cf66; color: white; padding: 1.5rem; 
                border-radius: 12px; text-align: center;">
        <h3>📦 Free Shipping</h3>
        <p>On orders over <strong>$50</strong></p>
        <p><em>Limited time offer</em></p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# ------------------------------------------
# 💬 Customer Testimonials
# ------------------------------------------
st.subheader("💬 What Our Customers Say")

col1, col2, col3 = st.columns(3)

testimonial_colors = ["#4DABF7", "#51cf66", "#ff6b6b"]
testimonials = [
    ("The AI recommendations are spot on! Found exactly what I needed.", "Sarah M."),
    ("Best shopping experience ever! The chatbot is super helpful.", "John D."),
    ("Love the personalized bundles! Saved me so much time.", "Emily R.")
]

for idx, (text, name) in enumerate(testimonials):
    with [col1, col2, col3][idx]:
        st.markdown(f"""
        <div style="background-color: #212529; padding: 1.5rem; border-radius: 10px;
                    border-left: 6px solid {testimonial_colors[idx]}; color: white;">
            <p style="font-size: 1rem;"><em>"{text}"</em></p>
            <p style="font-weight:bold; margin-top: 0.5rem;">- {name} ⭐⭐⭐⭐⭐</p>
        </div>
        """, unsafe_allow_html=True)

st.markdown("---")

# ------------------------------------------
# 📧 Newsletter Signup
# ------------------------------------------

from utils.email_service import send_welcome_email
# Newsletter signup
st.subheader("📧 Stay Updated")

col1, col2 = st.columns([2, 1])

with col1:
    email = st.text_input("Enter your email for exclusive deals", placeholder="your@email.com", key="newsletter_email")
    if st.button("Subscribe Now", type="primary"):
        if email:
            # Validate email format
            import re
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            
            if re.match(email_pattern, email):
                # Try to send email
                try:
                    import sys
                    from pathlib import Path
                    sys.path.append(str(Path(__file__).parent.parent))
                    from utils.email_service import send_welcome_email
                    
                    with st.spinner("Sending welcome email..."):
                        if send_welcome_email(email):
                            st.success("🎉 Thanks for subscribing! Check your inbox for a welcome offer.")
                            st.balloons()
                        else:
                            st.warning("⚠️ Subscription recorded, but email couldn't be sent. Please check your email configuration.")
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
                    st.info("💡 Make sure EMAIL_SERVICE_KEY is set in your .env file")
            else:
                st.error("❌ Please enter a valid email address")
        else:
            st.warning("⚠️ Please enter your email address")

with col2:
    st.info("""
    **Get 10% OFF**  
    on your first order when you subscribe!
    
    Use code: **WELCOME10**
    """)

st.markdown("---")

# ------------------------------------------
# 📊 Footer Stats
# ------------------------------------------
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Happy Customers", "10,000+", "+1,234")
with col2:
    st.metric("Products", "150+", "+12")
with col3:
    st.metric("Avg Rating", "4.6/5", "+0.2")
with col4:
    st.metric("Orders Today", "342", "+89")

st.markdown("---")
st.caption("© 2025 AI Shopping Agent | Powered by Advanced AI Technology | 🛡️ Secure Checkout")
