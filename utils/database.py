import json
from pathlib import Path
from datetime import datetime

class Database:
    """Simple JSON-based database for storing user data"""
    
    def __init__(self):
        self.data_dir = Path("data")
        self.data_dir.mkdir(exist_ok=True)
        
        self.products_file = self.data_dir / "products.json"
        self.users_file = self.data_dir / "users.json"
        self.carts_file = self.data_dir / "carts.json"
        self.history_file = self.data_dir / "browsing_history.json"
        self.wishlist_file = self.data_dir / "wishlist.json"
        self.alerts_file = self.data_dir / "price_alerts.json"
        self.price_history_file = self.data_dir / "price_history.json"
        
        # Initialize files if they don't exist
        self._init_files()
        self.seed_price_history()
    
    def _init_files(self):
        """Create empty data files if they don't exist"""
        if not self.users_file.exists():
            self._save_json(self.users_file, {})
        
        if not self.carts_file.exists():
            self._save_json(self.carts_file, {})
        
        if not self.history_file.exists():
            self._save_json(self.history_file, {})
            
        if not self.wishlist_file.exists():
            self._save_json(self.wishlist_file, {})
            
        if not self.alerts_file.exists():
            self._save_json(self.alerts_file, {})
            
        if not self.price_history_file.exists():
            self._save_json(self.price_history_file, {})
    
    def _load_json(self, file_path):
        """Load JSON file"""
        try:
            with open(file_path, 'r') as f:
                return json.load(f)
        except:
            return {}
    
    def _save_json(self, file_path, data: dict):
        """Save to JSON file"""
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)
    
    # Product operations
    def get_products(self):
        """Get all products"""
        return self._load_json(self.products_file)
    
    def get_product_by_id(self, product_id):
        """Get single product by ID"""
        products = self.get_products()
        for product in products:
            if product['id'] == product_id:
                return product
        return None
    
    # User operations
    def get_user(self, user_id):
        """Get user profile"""
        users = self._load_json(self.users_file)
        if user_id not in users:
            # Create new user
            users[user_id] = {
                "id": user_id,
                "preferences": {},
                "purchase_history": [],
                "created_at": datetime.now().isoformat()
            }
            self._save_json(self.users_file, users)
        return users[user_id]
    
    def update_user_preferences(self, user_id, preferences):
        """Update user preferences"""
        users = self._load_json(self.users_file)
        if user_id in users:
            users[user_id]['preferences'].update(preferences)
            self._save_json(self.users_file, users)
    
    def add_to_purchase_history(self, user_id, product_ids):
        """Add products to user's purchase history"""
        users = self._load_json(self.users_file)
        if user_id in users:
            users[user_id]['purchase_history'].extend(product_ids)
            self._save_json(self.users_file, users)
    
    # Cart operations
    def get_cart(self, user_id):
        """Get user's cart"""
        carts = self._load_json(self.carts_file)
        return carts.get(user_id, [])
    
    def update_cart(self, user_id, cart_items):
        """Update user's cart"""
        carts: dict = self._load_json(self.carts_file)
        carts[user_id] = cart_items
        self._save_json(self.carts_file, carts)
    
    def clear_cart(self, user_id):
        """Clear user's cart"""
        carts = self._load_json(self.carts_file)
        if user_id in carts:
            carts[user_id] = []
            self._save_json(self.carts_file, carts)
    
    # Browsing history
    def add_to_history(self, user_id, product_id):
        """Track product views"""
        history: dict = self._load_json(self.history_file)
        if user_id not in history:
            history[user_id] = []
        
        history[user_id].append({
            "product_id": product_id,
            "timestamp": datetime.now().isoformat()
        })
        
        # Keep only last 100 views
        history[user_id] = history[user_id][-100:]
        self._save_json(self.history_file, history)
    
    def get_browsing_history(self, user_id):
        """Get user's browsing history"""
        history = self._load_json(self.history_file)
        return history.get(user_id, [])

    # Wishlist operations
    def get_wishlist(self, user_id):
        """Get user's wishlist"""
        wishlist = self._load_json(self.wishlist_file)
        return wishlist.get(user_id, [])

    def update_wishlist(self, user_id, wishlist_items):
        """Update user's wishlist"""
        wishlist: dict = self._load_json(self.wishlist_file)
        wishlist[user_id] = wishlist_items
        self._save_json(self.wishlist_file, wishlist)

    # Price Alert operations
    def get_price_alerts(self, user_id):
        """Get user's active price alerts"""
        alerts = self._load_json(self.alerts_file)
        return alerts.get(user_id, [])

    def add_price_alert(self, user_id, product_id, target_price):
        """Add or update a price alert"""
        alerts = self._load_json(self.alerts_file)
        if user_id not in alerts:
            alerts[user_id] = []
        
        # Update if exists, else append
        existing = next((a for a in alerts[user_id] if a['product_id'] == product_id), None)
        if existing:
            existing['target_price'] = target_price
            existing['timestamp'] = datetime.now().isoformat()
        else:
            alerts[user_id].append({
                "product_id": product_id,
                "target_price": target_price,
                "timestamp": datetime.now().isoformat()
            })
        self._save_json(self.alerts_file, alerts)

    # Price History operations
    def track_price(self, product_id, price, site="Our Store"):
        """Record a price point for history"""
        history: dict = self._load_json(self.price_history_file)
        p_id = str(product_id)
        if p_id not in history:
            history[p_id] = []
        
        history[p_id].append({
            "price": price,
            "site": site,
            "timestamp": datetime.now().isoformat()
        })
        
        # Keep last 30 price points
        history[product_id] = history[product_id][-30:]
        self._save_json(self.price_history_file, history)

    def get_price_history(self, product_id):
        """Get price history for a product"""
        history = self._load_json(self.price_history_file)
        return history.get(str(product_id), [])

    def seed_price_history(self):
        """Pre-populate price history with mock data for demonstration"""
        history = self._load_json(self.price_history_file)
        if history: # Only seed if empty
            return
            
        products = self.get_products()
        import random
        from datetime import timedelta
        
        for product in products:
            p_id = str(product['id'])
            p_price = product['price']
            history[p_id] = []
            
            # Generate 7 days of history
            for i in range(7, 0, -1):
                timestamp = (datetime.now() - timedelta(days=i)).isoformat()
                # Simulate some fluctuation
                fluctuation = random.uniform(-0.1, 0.05) * p_price
                history[p_id].append({
                    "price": round(p_price + fluctuation, 2),
                    "site": "Market average",
                    "timestamp": timestamp
                })
        
        self._save_json(self.price_history_file, history)

# Create global database instance
db = Database()