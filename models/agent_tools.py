import json
from models.recommender import recommender
import streamlit as st
from utils.price_fetcher import fetch_external_prices
from utils.database import db

def get_bundles():
    """
    Useful for suggesting products that go well together with what's in the user's cart.
    """
    cart = st.session_state.get('cart', [])
    if not cart:
        return "The cart is empty, so I can't suggest a bundle yet. Try adding something first!"
    
    bundles = recommender.get_ai_bundle_proposals(cart)
    if not bundles:
        return "I couldn't find any specific bundle deals for your items right now."
        
    response = "Based on your cart, I recommend adding these as a bundle:\n\n"
    for b in bundles:
        response += f"- {b['name']} (${b['price']}) - {b['description']}\n"
    return response

def set_price_alert(product_name: str, target_price: float):
    """
    Useful for setting a notification when a product's price drops to a specific target.
    """
    try:
        # Resolve product name to ID using search
        search_results = recommender.get_hybrid_recommendations(product_name, n=1)
        if not search_results:
            return f"I couldn't find a product named '{product_name}' to monitor."
        
        product = search_results[0]
        db.add_price_alert(st.session_state.user_id, product['id'], target_price)
        return f"✅ Done! I'll monitor '{product['name']}' and alert you when the price drops to ${target_price:.2f} or lower."
    except Exception as e:
        return f"Error setting price alert: {str(e)}"

def get_savings_summary():
    """
    Useful for showing the user how much they could save on their wishlist items based on current market comparisons.
    """
    try:
        wishlist = st.session_state.get('wishlist', [])
        if not wishlist:
            return "Your wishlist is empty, so I don't have any savings to report yet!"
        
        total_potential_savings = 0
        details = ""
        
        for item in wishlist:
            prices = fetch_external_prices(item['name'])
            if prices:
                cheapest = prices[0]
                if cheapest['price'] < item['price']:
                    savings = item['price'] - cheapest['price']
                    total_potential_savings += savings
                    details += f"- **{item['name']}**: Save ${savings:.2f} by buying at {cheapest['site']} (${cheapest['price']:.2f})\n"
        
        if total_potential_savings > 0:
            return f"I found potential savings of **${total_potential_savings:.2f}** on your wishlist items!\n\n{details}"
        else:
            return "Based on my current search, our internal prices are already the best deals for your wishlist items!"
    except Exception as e:
        return f"Error calculating savings: {str(e)}"

def compare_prices(product_name: str):
    """
    Useful for finding the cheapest price for a product across different websites.
    """
    try:
        results = fetch_external_prices(product_name)
        if not results:
            return f"Could not find price comparisons for '{product_name}'."
        
        lines: list[str] = [f"I compared prices for '{product_name}' across several sites:\n"]
        for res in results:
            lines.append(f"- **{res['site']}**: {res['currency']}{res['price']}  \n  [View on {res['site']}]({res['url']})")
            # Track price in history for future charts
            search_results = recommender.get_hybrid_recommendations(product_name, n=1)
            if search_results:
                db.track_price(search_results[0]['id'], res['price'], res['site'])
        
        lines.append("\n*Sorted from cheapest to most expensive.*")
        return "\n".join(lines)
    except Exception as e:
        return f"Error comparing prices: {str(e)}"

def get_real_time_web_prices(product_name: str) -> str:
    """
    Conceptual bridge: Instructs the AI to perform a real-time web search for current prices.
    """
    return f"SEARCH_REQUIRED: Please perform an active web search for the current price of '{product_name}' at major retailers (Amazon, Walmart, Best Buy, eBay) and report the findings from cheapest to most expensive."

def search_products(query: str, n: int = 3):
    """
    Useful for finding products matching a semantic query or keyword search.
    """
    try:
        user_prefs = st.session_state.get('user_preferences', {})
        history = st.session_state.get('browsing_history', [])
        products = recommender.get_hybrid_recommendations(query, user_prefs, history, n)
        if not products:
            return "No matching products found."
        
        result = "Found products:\n"
        for p in products:
            result += f"- ID: {p['id']}, Name: {p['name']}, Price: ${p['price']}, Rating: {p['rating']}, Stock: {p['stock']}, Description: {p['description']}\n"
        return result
    except Exception as e:
        return f"Error searching products: {str(e)}"

def get_product_details(product_id: str):
    """
    Useful for getting the full details of a specific product by ID.
    """
    for p in recommender.products:
        if p['id'] == product_id:
            return json.dumps(p)
    return "Product not found."

def get_user_preferences():
    """
    Useful for finding out what the current user likes, their budget, and interests to tailor recommendations.
    """
    prefs = st.session_state.get('user_preferences', {})
    if not prefs or (not prefs.get('favorite_categories') and not prefs.get('interests')):
        return "User has no specific preferences set yet."
    return json.dumps(prefs)

def check_cart():
    """
    Useful for seeing what items the user currently has in their shopping cart.
    """
    cart = st.session_state.get('cart', [])
    if not cart:
        return "The shopping cart is empty."
    
    total = sum(item['price'] for item in cart)
    result = f"Cart contains {len(cart)} items. Total: ${total:.2f}\n"
    for item in cart:
         result += f"- {item['name']} (${item['price']})\n"
    return result

def add_to_cart(product_id: str):
    """
    Useful for adding a product to the user's shopping cart.
    """
    try:
        product = recommender.find_product_by_id(product_id)
        if not product:
            # Try to search for it if the ID wasn't exact
            search_results = recommender.get_hybrid_recommendations(product_id, n=1)
            if search_results:
                product = search_results[0]
            else:
                return f"Could not find product with ID or name '{product_id}'."
        
        if 'cart' not in st.session_state:
            st.session_state.cart = []
        st.session_state.cart.append(product)
        
        # Persistent storage
        db.update_cart(st.session_state.user_id, st.session_state.cart)
        
        return f"Successfully added {product['name']} to your cart."
    except Exception as e:
        return f"Error adding to cart: {str(e)}"

def remove_from_cart(product_id: str):
    """
    Useful for removing an item from the shopping cart.
    """
    try:
        if 'cart' not in st.session_state or not st.session_state.cart:
            return "Your cart is already empty."
        
        # Look for the product in the cart
        for i, item in enumerate(st.session_state.cart):
            if str(item['id']) == product_id or product_id.lower() in item['name'].lower():
                removed_item = st.session_state.cart.pop(i)
                # Persistent storage
                db.update_cart(st.session_state.user_id, st.session_state.cart)
                return f"Removed {removed_item['name']} from your cart."
        
        return f"Product '{product_id}' not found in your cart."
    except Exception as e:
        return f"Error removing from cart: {str(e)}"

def clear_cart():
    """
    Useful for emptying the user's shopping cart completely.
    """
    st.session_state.cart = []
    # Persistent storage
    db.clear_cart(st.session_state.user_id)
    return "Your shopping cart has been cleared."

# Register tools for OpenAI API
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "search_products",
            "description": "Searches the catalog for products based on a semantic query or keywords.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search query (e.g. 'wireless headphones', 'cheap skincare')."
                    },
                    "n": {
                        "type": "integer",
                        "description": "Number of results to return. Default 3."
                    }
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_product_details",
            "description": "Gets full JSON details for a specific product using its ID.",
            "parameters": {
                "type": "object",
                "properties": {
                    "product_id": {
                        "type": "string",
                        "description": "The product ID (e.g. 'p001')."
                    }
                },
                "required": ["product_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_user_preferences",
            "description": "Returns the logged-in user's shopping preferences, favorite categories, and budget constraints.",
            "parameters": {
                "type": "object",
                "properties": {}
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "add_to_cart",
            "description": "Adds a specific product to the user's shopping cart.",
            "parameters": {
                "type": "object",
                "properties": {
                    "product_id": {
                        "type": "string",
                        "description": "The ID or name of the product to add."
                    }
                },
                "required": ["product_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "remove_from_cart",
            "description": "Removes a specific product from the user's shopping cart.",
            "parameters": {
                "type": "object",
                "properties": {
                    "product_id": {
                        "type": "string",
                        "description": "The ID or name of the product to remove."
                    }
                },
                "required": ["product_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "clear_cart",
            "description": "Removes all items from the user's shopping cart.",
            "parameters": {
                "type": "object",
                "properties": {}
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "compare_prices",
            "description": "Compares real-time prices for a product across several websites to find the cheapest option.",
            "parameters": {
                "type": "object",
                "properties": {
                    "product_name": {
                        "type": "string",
                        "description": "The name of the product to compare prices for."
                    }
                },
                "required": ["product_name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "set_price_alert",
            "description": "Sets a target price alert for a product. AI will monitor and notify the user.",
            "parameters": {
                "type": "object",
                "properties": {
                    "product_name": {"type": "string", "description": "The name of the product to monitor."},
                    "target_price": {"type": "number", "description": "The target price threshold for the alert."}
                },
                "required": ["product_name", "target_price"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_savings_summary",
            "description": "Calculates and reports potential savings across all items in the user's wishlist.",
            "parameters": {
                "type": "object",
                "properties": {}
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_real_time_web_prices",
            "description": "Requests current, live web prices for any product using web search.",
            "parameters": {
                "type": "object",
                "properties": {
                    "product_name": {"type": "string", "description": "The name of the product to search for."}
                },
                "required": ["product_name"]
            }
        }
    }
]

# Mapping function names to actual Python functions
AVAILABLE_FUNCTIONS = {
    "search_products": search_products,
    "get_product_details": get_product_details,
    "get_user_preferences": get_user_preferences,
    "check_cart": check_cart,
    "add_to_cart": add_to_cart,
    "remove_from_cart": remove_from_cart,
    "clear_cart": clear_cart,
    "compare_prices": compare_prices,
    "get_bundles": get_bundles,
    "set_price_alert": set_price_alert,
    "get_savings_summary": get_savings_summary,
    "get_real_time_web_prices": get_real_time_web_prices
}
