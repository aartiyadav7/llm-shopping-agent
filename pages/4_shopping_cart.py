import streamlit as st
import pandas as pd

st.set_page_config(page_title="Shopping Cart", page_icon="🛒", layout="wide")

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
    </style>
""", unsafe_allow_html=True)

st.title("🛒 Your Shopping Cart")

# Initialize cart
if 'cart' not in st.session_state:
    st.session_state.cart = []

# Check if cart is empty
if len(st.session_state.cart) == 0:
    st.info("🛍️ Your cart is empty. Start shopping!")
    if st.button("Browse Products"):
        st.switch_page("pages/2_browse_products.py")
else:
    # Display cart items
    st.subheader(f"📦 {len(st.session_state.cart)} items in your cart")
    
    # Cart items display
    for idx, item in enumerate(st.session_state.cart):
        col1, col2, col3, col4 = st.columns([1, 3, 2, 1])
        
        with col1:
            st.markdown(f"<div style='font-size: 3rem; text-align: center;'>{item['image']}</div>", 
                       unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"**{item['name']}**")
            st.caption(item['category'])
            st.caption(f"⭐ {item['rating']}")
        
        with col3:
            st.markdown(f"### ${item['price']:.2f}")
        
        with col4:
            if st.button("🗑️", key=f"remove_{idx}"):
                st.session_state.cart.pop(idx)
                st.rerun()
        
        st.markdown("---")
    
    # Cart summary
    col1, col2 = st.columns([2, 1])
    
    with col2:
        subtotal = sum([item['price'] for item in st.session_state.cart])
        tax = subtotal * 0.08  # 8% tax
        shipping = 5.99 if subtotal < 50 else 0  # Free shipping over $50
        total = subtotal + tax + shipping
        
        st.markdown("""
        <div style="background-color: #f8f9fa; padding: 1.5rem; border-radius: 10px;">
        """, unsafe_allow_html=True)
        
        st.markdown("### 💰 Order Summary")
        st.write(f"Subtotal: ${subtotal:.2f}")
        st.write(f"Tax (8%): ${tax:.2f}")
        st.write(f"Shipping: ${shipping:.2f}" + (" ✨ FREE" if shipping == 0 else ""))
        st.markdown(f"### Total: ${total:.2f}")
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Promo code
        st.text_input("🎁 Promo Code", placeholder="Enter code")
        
        # Checkout button
        if st.button("✅ Proceed to Checkout", use_container_width=True, type="primary"):
            st.success("🎉 Order placed successfully!")
            st.balloons()
            st.session_state.cart = []
            st.info("Redirecting to home...")
    
    with col1:
        st.subheader("✨ Smart AI Bundles")
        st.info("💡 Our AI analyzed your cart and suggests these perfect additions:")
        
        from models.recommender import recommender
        ai_bundles = []
        if st.session_state.cart:
            ai_bundles = recommender.get_ai_bundle_proposals(st.session_state.cart)
        
        if ai_bundles:
            for bundle in ai_bundles:
                b_col1, b_col2 = st.columns([1, 4])
                with b_col1:
                    st.markdown(f"<div style='font-size: 2.5rem; text-align: center;'>{bundle['image']}</div>", unsafe_allow_html=True)
                with b_col2:
                    st.markdown(f"**{bundle['name']}** - ${bundle['price']}")
                    st.caption(bundle['description'])
                    if st.button("Add to Cart", key=f"add_bundle_{bundle['id']}"):
                        st.session_state.cart.append(bundle)
                        from utils.database import db
                        db.update_cart(st.session_state.user_id, st.session_state.cart)
                        st.success(f"Added {bundle['name']} to cart!")
                        st.rerun()
                st.markdown("---")
        else:
            st.write("Add more items to your cart to see personalized bundle deals!")