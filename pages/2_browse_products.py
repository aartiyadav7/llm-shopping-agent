import streamlit as st
import json
import pandas as pd
from pathlib import Path

st.set_page_config(page_title="Browse Products", page_icon="🛍️", layout="wide")
from utils.database import db
from utils.price_fetcher import fetch_external_prices

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
    
    .premium-card {
        background: white;
        padding: 1.5rem;
        border-radius: 20px;
        border: 1px solid #eef2f6;
        box-shadow: 0 10px 25px rgba(0, 0, 0, 0.03);
        transition: transform 0.3s ease;
    }
    </style>
""", unsafe_allow_html=True)

# Load products with error handling
@st.cache_data
def load_products():
    products_file = Path("data/products.json")
    if products_file.exists():
        try:
            with open(products_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if isinstance(data, list) and len(data) > 0:
                    return data
        except Exception as e:
            st.error(f"Error loading products: {e}")
    return []

products = load_products()

# Page header
st.title("🛍️ Browse Products")
st.markdown("Discover amazing products curated just for you!")

# Check if products exist
if len(products) == 0:
    st.error("⚠️ No products found! Please make sure `data/products.json` exists and contains product data.")
    st.info("📝 **How to fix:** Create a `data/products.json` file with product data. Check the README for the format.")
    st.stop()

# Filters
st.sidebar.header("🔍 Filters")

# Category filter
categories = list(set([p['category'] for p in products]))
selected_category = st.sidebar.selectbox("Category", ["All"] + sorted(categories))

# Price range filter
min_price = min([p['price'] for p in products])
max_price = max([p['price'] for p in products])
price_range = st.sidebar.slider("Price Range ($)", float(min_price), float(max_price), (float(min_price), float(max_price)))

# Rating filter
min_rating = st.sidebar.slider("Minimum Rating", 0.0, 5.0, 4.0, 0.5)

# Search
search_query = st.text_input("🔎 Search products...", placeholder="e.g., headphones, jeans, skincare")

# Filter products
filtered_products = products

if selected_category != "All":
    filtered_products = [p for p in filtered_products if p['category'] == selected_category]

filtered_products = [p for p in filtered_products 
                     if price_range[0] <= p['price'] <= price_range[1] 
                     and p['rating'] >= min_rating]

if search_query:
    filtered_products = [p for p in filtered_products 
                         if search_query.lower() in p['name'].lower() 
                         or search_query.lower() in ' '.join(p['tags']).lower()]

# Display results count
st.markdown(f"### Found {len(filtered_products)} products")

# Display products in grid
if len(filtered_products) > 0:
    cols_per_row = 3
    rows = len(filtered_products) // cols_per_row + (1 if len(filtered_products) % cols_per_row != 0 else 0)

    for row in range(rows):
        cols = st.columns(cols_per_row)
        
        for col_idx in range(cols_per_row):
            product_idx = row * cols_per_row + col_idx
            
            if product_idx < len(filtered_products):
                product = filtered_products[product_idx]
                
                with cols[col_idx]:
                    # Get market comparison
                    ext_prices = fetch_external_prices(product['name'])
                    best_web_price = ext_prices[0]['price'] if ext_prices else product['price']
                    
                    st.markdown(f"""
                    <div class="premium-card">
                        <div style="font-size: 4rem; text-align: center; margin-bottom: 1rem;">{product['image']}</div>
                        <h4 style="margin: 0;">{product['name']}</h4>
                        <p style="color: #718096; font-size: 0.8rem; margin-bottom: 0.5rem;">{product['category']}</p>
                        <div style="display: flex; justify-content: space-between; align-items: center; margin: 1rem 0;">
                            <span style="font-size: 1.5rem; font-weight: bold; color: #4DABF7;">${product['price']:.2f}</span>
                            <span style="font-size: 0.7rem; background: rgba(77, 171, 247, 0.1); color: #4DABF7; padding: 4px 10px; border-radius: 20px; border: 1px solid rgba(77, 171, 247, 0.2);">
                                🌐 Market: ${best_web_price:.2f}
                            </span>
                        </div>
                        <div style="display: flex; gap: 0.5rem; margin-bottom: 1rem; font-size: 0.8rem;">
                            <span style="color: #f59f00;">⭐ {product['rating']}</span>
                            <span style="color: #718096;">|</span>
                            <span style="color: {'#48bb78' if product['stock'] > 10 else '#f56565'};">
                                {'In Stock' if product['stock'] > 0 else 'Out of Stock'}
                            </span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    st.caption(f"📦 {product['stock']} units available")
                    
                    # Add to cart button
                    if st.button(f"Add to Cart", key=f"add_{product['id']}", use_container_width=True):
                        if 'cart' not in st.session_state:
                            st.session_state.cart = []
                        
                        st.session_state.cart.append(product)
                        
                        # Sync to DB
                        db.update_cart(st.session_state.user_id, st.session_state.cart)
                        
                        # Track browsing history
                        if 'browsing_history' not in st.session_state:
                            st.session_state.browsing_history = []
                        st.session_state.browsing_history.append(product['id'])
                        db.add_to_history(st.session_state.user_id, product['id'])
                        
                        st.success(f"✅ Added {product['name']} to cart!")
                        st.rerun()
                    
                    # Add to Wishlist
                    if st.button(f"🤍 Wishlist", key=f"wish_{product['id']}", use_container_width=True):
                        if 'wishlist' not in st.session_state:
                            st.session_state.wishlist = []
                        
                        if product['id'] not in [p['id'] for p in st.session_state.wishlist]:
                            st.session_state.wishlist.append(product)
                            db.update_wishlist(st.session_state.user_id, st.session_state.wishlist)
                            st.success(f"💖 Added {product['name']} to wishlist!")
                        else:
                            st.info("Already in wishlist")
                    
                    # Quick view details
                    with st.expander("View Details"):
                        st.write(product['description'])
                        st.write(f"**Tags:** {', '.join(product['tags'])}")
else:
    # Empty state
    st.info("😔 No products found. Try adjusting your filters!")

# Show cart summary in sidebar
st.sidebar.markdown("---")
st.sidebar.subheader("🛒 Your Cart")
if 'cart' in st.session_state and len(st.session_state.cart) > 0:
    cart_total = sum([item['price'] for item in st.session_state.cart])
    st.sidebar.success(f"**{len(st.session_state.cart)} items** - Total: ${cart_total:.2f}")
    if st.sidebar.button("Go to Cart"):
        st.switch_page("pages/4_shopping_cart.py")
else:
    st.sidebar.info("Cart is empty")