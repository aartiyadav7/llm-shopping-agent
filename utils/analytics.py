import json
from pathlib import Path
from datetime import datetime
from collections import Counter

class Analytics:
    """Track user behavior and generate insights"""
    
    def __init__(self):
        self.analytics_file = Path("data/analytics.json")
        self._init_analytics()
    
    def _init_analytics(self):
        """Initialize analytics file"""
        if not self.analytics_file.exists():
            initial_data = {
                "page_views": [],
                "product_clicks": [],
                "cart_additions": [],
                "purchases": [],
                "search_queries": [],
                "chat_interactions": []
            }
            self._save_analytics(initial_data)
    
    def _load_analytics(self):
        """Load analytics data"""
        try:
            with open(self.analytics_file, 'r') as f:
                return json.load(f)
        except:
            return {}
    
    def _save_analytics(self, data):
        """Save analytics data"""
        with open(self.analytics_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def track_page_view(self, user_id, page_name):
        """Track when user visits a page"""
        data = self._load_analytics()
        data['page_views'].append({
            "user_id": user_id,
            "page": page_name,
            "timestamp": datetime.now().isoformat()
        })
        self._save_analytics(data)
    
    def track_product_click(self, user_id, product_id):
        """Track when user clicks on a product"""
        data = self._load_analytics()
        data['product_clicks'].append({
            "user_id": user_id,
            "product_id": product_id,
            "timestamp": datetime.now().isoformat()
        })
        self._save_analytics(data)
    
    def track_cart_addition(self, user_id, product_id, product_name, price):
        """Track when user adds item to cart"""
        data = self._load_analytics()
        data['cart_additions'].append({
            "user_id": user_id,
            "product_id": product_id,
            "product_name": product_name,
            "price": price,
            "timestamp": datetime.now().isoformat()
        })
        self._save_analytics(data)
    
    def track_purchase(self, user_id, product_ids, total_amount):
        """Track completed purchases"""
        data = self._load_analytics()
        data['purchases'].append({
            "user_id": user_id,
            "product_ids": product_ids,
            "total_amount": total_amount,
            "timestamp": datetime.now().isoformat()
        })
        self._save_analytics(data)
    
    def track_search(self, user_id, search_query):
        """Track search queries"""
        data = self._load_analytics()
        data['search_queries'].append({
            "user_id": user_id,
            "query": search_query,
            "timestamp": datetime.now().isoformat()
        })
        self._save_analytics(data)
    
    def track_chat_interaction(self, user_id, user_message, ai_response):
        """Track chat conversations"""
        data = self._load_analytics()
        data['chat_interactions'].append({
            "user_id": user_id,
            "user_message": user_message,
            "ai_response": ai_response[:100],  # Store first 100 chars
            "timestamp": datetime.now().isoformat()
        })
        self._save_analytics(data)
    
    def get_popular_products(self, n=10):
        """Get most clicked/added products"""
        data = self._load_analytics()
        
        # Count product clicks
        product_clicks = [item['product_id'] for item in data.get('product_clicks', [])]
        cart_additions = [item['product_id'] for item in data.get('cart_additions', [])]
        
        all_interactions = product_clicks + cart_additions
        counter = Counter(all_interactions)
        
        return counter.most_common(n)
    
    def get_user_insights(self, user_id):
        """Get insights about a specific user"""
        data = self._load_analytics()
        
        insights = {
            "total_page_views": 0,
            "total_product_clicks": 0,
            "total_cart_additions": 0,
            "total_purchases": 0,
            "favorite_categories": [],
            "avg_order_value": 0
        }
        
        # Count activities
        insights['total_page_views'] = len([
            p for p in data.get('page_views', []) if p['user_id'] == user_id
        ])
        
        insights['total_product_clicks'] = len([
            p for p in data.get('product_clicks', []) if p['user_id'] == user_id
        ])
        
        insights['total_cart_additions'] = len([
            p for p in data.get('cart_additions', []) if p['user_id'] == user_id
        ])
        
        user_purchases = [
            p for p in data.get('purchases', []) if p['user_id'] == user_id
        ]
        insights['total_purchases'] = len(user_purchases)
        
        # Calculate average order value
        if user_purchases:
            total_spent = sum([p['total_amount'] for p in user_purchases])
            insights['avg_order_value'] = total_spent / len(user_purchases)
        
        return insights
    
    def get_trending_searches(self, n=5):
        """Get most common search queries"""
        data = self._load_analytics()
        queries = [item['query'] for item in data.get('search_queries', [])]
        counter = Counter(queries)
        return counter.most_common(n)
    
    def get_conversion_rate(self):
        """Calculate cart-to-purchase conversion rate"""
        data = self._load_analytics()
        
        cart_count = len(data.get('cart_additions', []))
        purchase_count = len(data.get('purchases', []))
        
        if cart_count == 0:
            return 0
        
        return (purchase_count / cart_count) * 100

# Create global analytics instance
analytics = Analytics()