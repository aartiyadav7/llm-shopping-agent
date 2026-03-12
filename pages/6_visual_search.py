import streamlit as st
import os
import base64
from openai import OpenAI
from dotenv import load_dotenv
from models.recommender import recommender
from io import BytesIO

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

st.set_page_config(page_title="Visual Search", page_icon="📸", layout="wide")

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
    
    .upload-container {
        background: white;
        padding: 2rem;
        border-radius: 20px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.05);
        border: 1px solid #eef2f6;
    }
    </style>
""", unsafe_allow_html=True)

st.title("📸 Visual Search: Shop the Look")
st.markdown("Upload a picture of an item you love, and we'll find similar products in our catalog using state-of-the-art visual AI!")

uploaded_file = st.file_uploader("Upload an image (JPG, PNG)", type=['jpg', 'jpeg', 'png'])

if uploaded_file is not None:
    # Display the uploaded image
    st.image(uploaded_file, caption="Your inspiration", width=400)
    
    if st.button("🔍 Find Similar Products", type="primary"):
        if not os.getenv("OPENAI_API_KEY"):
            st.error("OpenAI API key is required to use Visual Search.")
        else:
            with st.spinner("Analyzing image and finding matches..."):
                try:
                    # Convert image to base64
                    base64_image = base64.b64encode(uploaded_file.getvalue()).decode('utf-8')
                    image_format = uploaded_file.type
                    
                    # 1. Use GPT-4o vision to extract a detailed semantic description
                    response = client.chat.completions.create(
                        model="gpt-4o",
                        messages=[
                            {
                                "role": "user",
                                "content": [
                                    {"type": "text", "text": "Describe the main item in this image in extreme detail (color, style, shape, material). Focus on details that would be useful for finding a similar product in an e-commerce catalog. Make it a terse string of keywords and concise phrases."},
                                    {
                                        "type": "image_url",
                                        "image_url": {
                                            "url": f"data:{image_format};base64,{base64_image}",
                                            "detail": "low"
                                        }
                                    }
                                ]
                            }
                        ],
                        max_tokens=100
                    )
                    
                    description = response.choices[0].message.content
                    st.info(f"**AI Vision Identified:** {description}", icon="👁️")
                    
                    # 2. Feed the rich visual description into our semantic recommender
                    user_prefs = st.session_state.get('user_preferences', {})
                    history = st.session_state.get('browsing_history', [])
                    results = recommender.get_hybrid_recommendations(description, user_preferences=user_prefs, browsing_history=history, n=4)
                    
                    if results:
                        st.success("Here are the closest matches from our catalog!")
                        cols = st.columns(4)
                        for i, p in enumerate(results):
                            with cols[i % 4]:
                                st.markdown(f"### {p['image']}")
                                st.markdown(f"**{p['name']}**")
                                st.markdown(f"${p['price']} | ⭐ {p['rating']}")
                                st.caption(p['description'])
                                if st.button("View Details", key=f"vs_{p['id']}"):
                                    st.session_state['selected_product'] = p['id']
                                    st.switch_page("pages/2_browse_products.py")
                    else:
                        st.warning("We couldn't find any close matches in our catalog right now.")
                        
                except Exception as e:
                    st.error(f"Error processing image: {e}")
                    
st.markdown("---")
st.caption("How it works: Our AI analyzes your image to understand its visual properties, then securely searches our product vector database for the closest semantic matches.")
