import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime

st.set_page_config(page_title="Profile", page_icon="👤", layout="wide")
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

    .stButton>button {
        border-radius: 12px !important;
        transition: all 0.3s !important;
    }
    
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 20px;
        box-shadow: 0 10px 25px rgba(0,0,0,0.03);
        border: 1px solid #eef2f6;
    }
    </style>
""", unsafe_allow_html=True)

st.title("👤 Your Profile & Preferences")

# Initialize user preferences
if 'user_preferences' not in st.session_state:
    st.session_state.user_preferences = {
        'favorite_categories': [],
        'budget_range': [0, 200],
        'shopping_frequency': 'Weekly',
        'interests': []
    }

# Profile tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 Overview", "💖 Wishlist", "⚙️ Preferences", "📈 Insights", "💰 Smart Savings"])

with tab1:
    st.subheader("Welcome back! 👋")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Purchases", "12", "+3 this month")
    with col2:
        st.metric("Money Saved", "$234", "+$45")
    with col3:
        st.metric("Items in Cart", len(st.session_state.get('cart', [])))
    with col4:
        st.metric("Wishlist", "8 items")
    
    st.markdown("---")
    
    # Recent activity
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🛍️ Recent Purchases")
        st.markdown("""
        - 🎧 Wireless Headphones - $79.99 (Oct 1)
        - 👕 Cotton T-Shirt - $24.99 (Sep 28)
        - 🧴 Face Cream - $39.99 (Sep 25)
        - ⌚ Smart Watch - $149.99 (Sep 20)
        """)
    
    with col2:
        st.subheader("⭐ Favorite Categories")
        categories = {
            'Electronics': 40,
            'Clothing': 25,
            'Skincare': 20,
            'Sports': 15
        }
        fig = go.Figure(data=[go.Pie(
            labels=list(categories.keys()),
            values=list(categories.values()),
            hole=0.3
        )])
        fig.update_layout(height=300, showlegend=True)
        st.plotly_chart(fig, use_container_width=True)

with tab2:
    st.subheader("💖 Your Wishlist")
    wishlist = st.session_state.get('wishlist', [])
    
    if not wishlist:
        st.info("Your wishlist is empty. Start adding items from the catalog!")
    else:
        for i, item in enumerate(wishlist):
            with st.container():
                col1, col2, col3 = st.columns([1, 3, 2])
                with col1:
                    st.markdown(f"<div style='font-size: 3rem;'>{item['image']}</div>", unsafe_allow_html=True)
                with col2:
                    st.markdown(f"**{item['name']}**")
                    st.write(f"Category: {item['category']} | Price: ${item['price']}")
                    if st.button(f"Remove", key=f"rem_wish_{item['id']}"):
                        st.session_state.wishlist.pop(i)
                        db.update_wishlist(st.session_state.user_id, st.session_state.wishlist)
                        st.rerun()
                with col3:
                    # Real Price History
                    history = db.get_price_history(item['id'])
                    
                    if len(history) > 1:
                        # Extract data for plotting
                        history_dates = [h['timestamp'][:10] for h in history]
                        history_prices = [h['price'] for h in history]
                        
                        fig = px.line(x=history_dates, y=history_prices, title="Price Trend")
                        fig.update_layout(height=150, margin=dict(l=0, r=0, t=30, b=0), showlegend=False)
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.caption("No price history yet. Compare prices to build data!")
                st.markdown("---")

with tab3:
    st.subheader("⚙️ Customize Your Experience")
    
    # Shopping preferences
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Shopping Preferences")
        
        favorite_categories = st.multiselect(
            "Favorite Categories",
            ["Electronics", "Clothing", "Footwear", "Skincare", "Sports", "Accessories"],
            default=st.session_state.user_preferences.get('favorite_categories', [])
        )
        
        budget_range = st.slider(
            "Budget Range ($)",
            0, 500, 
            st.session_state.user_preferences.get('budget_range', [0, 200])
        )
        
        shopping_frequency = st.selectbox(
            "Shopping Frequency",
            ["Daily", "Weekly", "Monthly", "Occasionally"],
            index=["Daily", "Weekly", "Monthly", "Occasionally"].index(
                st.session_state.user_preferences.get('shopping_frequency', 'Weekly')
            )
        )
    
    with col2:
        st.markdown("### Interests & Tags")
        
        interests = st.multiselect(
            "What are you interested in?",
            ["Fitness", "Fashion", "Tech", "Beauty", "Outdoor", "Gaming", "Health"],
            default=st.session_state.user_preferences.get('interests', [])
        )
        
        st.markdown("### Notifications")
        email_deals = st.checkbox("Email me about deals", value=True)
        email_restock = st.checkbox("Notify when items restock", value=True)
        email_recommendations = st.checkbox("Send personalized recommendations", value=True)
    
    # Save preferences button
    if st.button("💾 Save Preferences", type="primary", use_container_width=True):
        st.session_state.user_preferences = {
            'favorite_categories': favorite_categories,
            'budget_range': budget_range,
            'shopping_frequency': shopping_frequency,
            'interests': interests
        }
        # Sync to DB
        db.update_user_preferences(st.session_state.user_id, st.session_state.user_preferences)
        st.success("✅ Preferences saved successfully!")
        st.balloons()

with tab4:
    st.subheader("📈 Your Shopping Insights")
    
    # Spending over time
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 💰 Monthly Spending")
        months = ['Jul', 'Aug', 'Sep', 'Oct']
        spending = [180, 240, 320, 290]
        
        fig = go.Figure(data=[
            go.Bar(x=months, y=spending, marker_color='#4DABF7')
        ])
        fig.update_layout(height=300, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("### 🏆 Shopping Score")
        score = 87
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=score,
            title={'text': "AI Confidence"},
            gauge={'axis': {'range': [0, 100]},
                   'bar': {'color': "#51cf66"},
                   'steps': [
                       {'range': [0, 50], 'color': "#ffe066"},
                       {'range': [50, 75], 'color': "#a9e34b"},
                       {'range': [75, 100], 'color': "#51cf66"}
                   ]}
        ))
        fig.update_layout(height=300)
        st.plotly_chart(fig, use_container_width=True)
    
    # Recommendations accuracy
    st.markdown("### 🎯 AI Recommendations Accuracy")
    st.progress(0.94)
    st.caption("The AI is 94% accurate in predicting products you'll love!")
    
    # Most viewed products
    st.markdown("### 👀 Most Viewed Products")
    viewed_products = [
        {"name": "Wireless Headphones", "views": 12},
        {"name": "Smart Watch", "views": 8},
        {"name": "Yoga Mat", "views": 6},
        {"name": "Face Cream", "views": 5},
    ]
    
    for product in viewed_products:
        col1, col2 = st.columns([3, 1])
        with col1:
            st.write(f"**{product['name']}**")
        with col2:
            st.write(f"{product['views']} views")
        st.progress(product['views'] / 12)

with tab5:
    st.subheader("💰 Smart Savings Dashboard")
    st.markdown("### 📉 Active Price Alerts")
    
    alerts = db.get_price_alerts(st.session_state.user_id)
    if not alerts:
        st.info("No active price alerts. Ask the AI Assistant to monitor a product for you!")
    else:
        for alert in alerts:
            product = db.get_product_by_id(alert['product_id'])
            if product:
                with st.container():
                    col1, col2, col3 = st.columns([1, 3, 2])
                    with col1:
                        st.markdown(f"<div style='font-size: 2rem;'>{product['image']}</div>", unsafe_allow_html=True)
                    with col2:
                        st.markdown(f"**{product['name']}**")
                        st.write(f"Target: ${alert['target_price']:.2f} | Current: ${product['price']:.2f}")
                    with col3:
                        if product['price'] <= alert['target_price']:
                            st.success("🎯 Target Reached!")
                        else:
                            st.info("⌛ Monitoring...")
                st.markdown("---")

    st.markdown("### 🏷️ Best External Deals (Wishlist)")
    wishlist = st.session_state.get('wishlist', [])
    if not wishlist:
        st.write("Add items to your wishlist to see market comparisons.")
    else:
        for item in wishlist:
            # Reusing fetch_external_prices but showing the best deal
            ext_prices = fetch_external_prices(item['name'])
            if ext_prices:
                cheapest = ext_prices[0]
                if cheapest['price'] < item['price']:
                    st.markdown(f"""
                    <div style="background: rgba(81, 207, 102, 0.1); padding: 15px; border-radius: 10px; border-left: 5px solid #51cf66; margin-bottom: 10px;">
                        <strong>🔥 Price Alert!</strong> {item['name']} is available for <strong>${cheapest['price']:.2f}</strong> at <strong>{cheapest['site']}</strong>! 
                        <br><small>That's ${item['price'] - cheapest['price']:.2f} cheaper than our current price.</small>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.write(f"✅ Our price for **{item['name']}** is currently the best in the market.")

# Sidebar actions
st.sidebar.header("🎯 Quick Actions")

if st.sidebar.button("🎁 Get Personalized Recommendations"):
    st.sidebar.success("Check the Chat Assistant for recommendations!")

if st.sidebar.button("📧 Request Product Recommendations"):
    st.sidebar.info("Recommendations sent to your email!")

if st.sidebar.button("🔄 Reset All Preferences"):
    st.session_state.user_preferences = {
        'favorite_categories': [],
        'budget_range': [0, 200],
        'shopping_frequency': 'Weekly',
        'interests': []
    }
    st.sidebar.warning("Preferences reset!")
    st.rerun()