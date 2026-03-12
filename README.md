# 🛍️ AI Shopping Agent

A state-of-the-art AI-powered shopping assistant that provides a premium, intelligent, and persistent e-commerce experience.

## 🚀 Key Features

*   **📸 Visual AI Search**: Upload images to find similar products using GPT-4o Vision.
*   **🧠 Persistent Intelligence**: User profiles, carts, and wishlists are saved across sessions using a local JSON database.
*   **🎁 Dynamic AI Bundling**: Real-time analysis of cart contents to suggest perfect product pairings.
*   **💰 Price Comparison Engine**: Live price fetching from Amazon, eBay, Best Buy, and Walmart, sorted from cheapest to premium.
*   **💎 Premium UI**: Modern glassmorphism design with vibrant gradients and optimized typography (Outfit font).
*   **📍 Smart Savings**: Interactive price history charts and automated deal monitoring.

## 🛠️ Tech Stack

- **Frontend**: Streamlit
- **Brain**: OpenAI GPT-4 (Vision & Tools), GPT-3.5-turbo (Reasoning)
- **Database**: Local JSON-based Persistent DB
- **Styling**: Vanilla CSS (Premium Glassmorphism)
- **Intelligence**: Hybrid Vector Search + LLM Reasoning

## 📂 Project Structure

- `app.py`: Main application entry point.
- `models/`: Agent tools and recommendation logic.
- `pages/`: Individual streamlit pages (Catalog, Cart, Profile, etc.).
- `utils/`: Core utilities (Price fetcher, Database, Email service).
- `data/`: Persistent storage for products and user data.

## 🏃 Quick Start

1.  **Clone the project**
2.  **Create a virtual environment**: `python -m venv venv`
3.  **Install dependencies**: `pip install -r requirements.txt`
4.  **Set up `.env`**: Add your `OPENAI_API_KEY`.
5.  **Run the app**: `streamlit run app.py`

---
*Built with ❤️ by AI Shopping Agent Team*
