import json
from pathlib import Path
from collections import Counter
import random
import os
from openai import OpenAI
from dotenv import load_dotenv
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

# Load environment variables
load_dotenv()

class ProductRecommender:
    """AI-powered product recommendation engine"""
    
    def __init__(self):
        self.products = self._load_products()
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.embeddings_cache_file = Path("data/product_embeddings.json")
        self.product_embeddings: dict = self._load_embeddings_cache()
        
    def _load_products(self):
        """Load products from JSON"""
        products_file = Path("data/products.json")
        if products_file.exists():
            try:
                with open(products_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        return data
            except Exception as e:
                print(f"Error loading products: {e}")
        return []

    def find_product_by_id(self, product_id: str):
        """Helper to find a product object by ID"""
        for p in self.products:
            if str(p.get('id')) == product_id:
                return p
        return None

    def _load_embeddings_cache(self):
        """Load cached embeddings if they exist"""
        if self.embeddings_cache_file.exists():
            try:
                with open(self.embeddings_cache_file, 'r') as f:
                    return json.load(f)
            except:
                return {}
        return {}

    def _save_embeddings_cache(self):
        """Save embeddings to cache"""
        with open(self.embeddings_cache_file, 'w') as f:
            json.dump(self.product_embeddings, f)

    def get_embedding(self, text):
        """Get embedding for a piece of text with fallback"""
        if not os.getenv("OPENAI_API_KEY"):
            return None
        try:
            # Use a short timeout to prevent hanging
            response = self.client.embeddings.create(
                input=text,
                model="text-embedding-3-small",
                timeout=5.0
            )
            return response.data[0].embedding
        except Exception as e:
            print(f"Error getting embedding: {e}")
            return None

    def update_product_embeddings(self):
        """Pre-calculate embeddings for all products"""
        if not os.getenv("OPENAI_API_KEY"):
            return
        
        updated = False
        for product in self.products:
            if product['id'] not in self.product_embeddings:
                text = f"{product['name']} {product['description']} {' '.join(product['tags'])}"
                embedding = self.get_embedding(text)
                if embedding:
                    self.product_embeddings[product['id']] = embedding
                    updated = True
                else:
                    # Break early if API is failing to avoid massive timeouts
                    break
        
        if updated:
            self._save_embeddings_cache()

    def get_semantic_recommendations(self, query, n=5):
        """Find products similar to the query using embeddings with fallback"""
        query_embedding = self.get_embedding(query)
        if not query_embedding:
            # Fallback: simple keyword matching if semantic search fails
            results = [p for p in self.products if query.lower() in p['name'].lower() or query.lower() in p['description'].lower()]
            return results[:n], {p['id']: 0.5 for p in results}

        self.update_product_embeddings()

        similarities = {}
        for product_id, embedding in self.product_embeddings.items():
            if isinstance(embedding, list):
                sim = cosine_similarity([query_embedding], [embedding])[0][0]
                similarities[product_id] = float(sim)

        top_ids = sorted(similarities.keys(), key=lambda x: similarities.get(x, 0), reverse=True)[:n]
        return [p for p in self.products if p['id'] in top_ids], similarities

    def get_hybrid_recommendations(self, query, user_preferences=None, browsing_history=None, n=5):
        """Combine semantic similarity with business rules and user history"""
        # Get semantic results and similarities (will handle fallback internally)
        _, similarities = self.get_semantic_recommendations(query, n=len(self.products))
        
        final_scores: dict[str, float] = {}
        for product in self.products:
            p_id = str(product['id'])
            # Start with semantic similarity (scaled to 0-50)
            score: float = similarities.get(p_id, 0.0) * 50
            
            # If no semantic score (fallback), use category/tag match boost
            if similarities.get(p_id) == 0.5:
                 score = 25.0 # Intermediate score for keyword matches
            
            # Metadata-based boosts
            # Rating boost (up to 10)
            score += float(product.get('rating', 0.0)) * 2
            
            # Stock availability boost (up to 5)
            stock = int(product.get('stock', 0))
            if stock > 100:
                score += 5.0
            elif stock > 0:
                score += 2.0
                
            # User Preference boost
            if user_preferences:
                if 'favorite_categories' in user_preferences:
                    if product.get('category') in user_preferences['favorite_categories']:
                        score += 10.0
                
                if 'budget_range' in user_preferences:
                    budget_range = user_preferences.get('budget_range')
                    if budget_range and len(budget_range) == 2:
                        min_b, max_b = budget_range
                        price = float(product.get('price', 0.0))
                        if min_b <= price <= max_b:
                            score += 5.0
                        else:
                            score -= 5.0

            # Browsing History boost
            if browsing_history and p_id in browsing_history:
                score += 5.0

            final_scores[p_id] = score

        top_ids = sorted(final_scores.keys(), key=lambda x: final_scores.get(x, 0), reverse=True)[:n]
        return [p for p in self.products if p['id'] in top_ids]

    def get_personalized_recommendations(self, user_preferences, browsing_history, n=5):
        """
        Original rule-based recommendations (kept for backward compatibility)
        """
        scores: dict[str, float] = {}
        
        for product in self.products:
            score: float = 0.0
            
            # Score based on favorite categories
            if 'favorite_categories' in user_preferences:
                if product['category'] in user_preferences['favorite_categories']:
                    score += 10
            
            # Score based on interests/tags
            interests = user_preferences.get('interests', [])
            if interests:
                for interest in interests:
                    interest_str = str(interest).lower()
                    product_tags = [str(tag).lower() for tag in product.get('tags', [])]
                    if interest_str in product_tags:
                        score += 5
            
            # Score based on budget
            if 'budget_range' in user_preferences:
                min_budget, max_budget = user_preferences['budget_range']
                if min_budget <= product['price'] <= max_budget:
                    score += 8
                else:
                    score -= 3  # Penalize out-of-budget items
            
            # Score based on rating
            score += product['rating'] * 2
            
            # Boost if similar to browsing history
            if browsing_history:
                viewed_products = [p for p in self.products if p['id'] in browsing_history]
                for viewed in viewed_products:
                    # Same category
                    if viewed['category'] == product['category']:
                        score += 3
                    # Similar tags
                    common_tags = set(product.get('tags', [])) & set(viewed.get('tags', []))
                    score += int(len(common_tags) * 2)
            
            scores[product['id']] = score
        
        # Get top N products
        top_product_ids = sorted(scores.keys(), key=lambda x: scores.get(x, 0), reverse=True)[:n]
        recommendations = [p for p in self.products if p['id'] in top_product_ids]
        
        return recommendations
    
    def get_ai_bundle_proposals(self, cart_items, n=2):
        """
        Uses LLM to reason about which products would make a great bundle 
        with the items currently in the cart.
        """
        if not cart_items or not os.getenv("OPENAI_API_KEY"):
            return []
            
        cart_desc = ", ".join([f"{item['name']} ({item['category']})" for item in cart_items])
        catalog_brief = "\n".join([f"- {p['id']}: {p['name']} ({p['category']})" for p in self.products])
        
        prompt = f"""
        The user has these items in their cart: {cart_desc}
        
        Based on our catalog, suggest {n} products that would perfectly complement these.
        Consider style, category logic (e.g., tech needs cables, shoes need socks), and user value.
        
        Catalog:
        {catalog_brief}
        
        Return ONLY a JSON list of product IDs. Example: ["p001", "p005"]
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=20,
                temperature=0.3
            )
            import re
            ids = re.findall(r'p\d{3}', response.choices[0].message.content)
            return [p for p in self.products if p['id'] in ids]
        except Exception as e:
            print(f"Error in AI bundling: {e}")
            return []

    def get_bundle_recommendations(self, product_id, n=3):
        """
        Get products that go well together (bundle recommendations)
        """
        main_product = next((p for p in self.products if p['id'] == product_id), None)
        
        if not main_product:
            return []
        
        bundle_ids = main_product.get('bundle_with', [])
        bundle_products = [p for p in self.products if p['id'] in bundle_ids]
        
        if len(bundle_products) < n:
            similar = self.find_similar_products(product_id, n - len(bundle_products))
            bundle_products.extend(similar)
        
        return bundle_products[:n]
    
    def find_similar_products(self, product_id, n=5):
        """
        Find similar products based on category and tags
        """
        main_product = next((p for p in self.products if p['id'] == product_id), None)
        
        if not main_product:
            return []
        
        similarity_scores = {}
        
        for product in self.products:
            if product['id'] == product_id:
                continue
            
            score = 0
            if product['category'] == main_product['category']:
                score += 10
            
            common_tags = set(product['tags']) & set(main_product['tags'])
            score += len(common_tags) * 3
            
            price_diff = abs(product['price'] - main_product['price']) / main_product['price']
            if price_diff < 0.3:
                score += 5
            
            similarity_scores[product['id']] = score
        
        top_ids = sorted(similarity_scores.keys(), key=lambda x: similarity_scores.get(x, 0), reverse=True)[:n]
        return [p for p in self.products if p['id'] in top_ids]
    
    def get_trending_products(self, n=10):
        """Get trending products (high rating + stock availability)"""
        scored_products = []
        for product in self.products:
            score = product['rating'] * (1 + (product['stock'] / 200))
            scored_products.append((product, score))
        
        scored_products.sort(key=lambda x: x[1], reverse=True)
        return [p[0] for p in scored_products[:n]]
    
    def get_category_recommendations(self, category, user_preferences=None, n=5):
        """Get best products in a category"""
        category_products = [p for p in self.products if p['category'] == category]
        if user_preferences and 'budget_range' in user_preferences:
            min_budget, max_budget = user_preferences['budget_range']
            category_products = [p for p in category_products 
                                if min_budget <= p['price'] <= max_budget]
        
        category_products.sort(key=lambda x: x['rating'], reverse=True)
        return category_products[:n]
    
    def get_frequently_bought_together(self, product_ids):
        """Get products frequently bought together"""
        all_bundle_products = []
        for product_id in product_ids:
            product = next((p for p in self.products if p['id'] == product_id), None)
            if product:
                bundle_ids = product.get('bundle_with', [])
                all_bundle_products.extend(bundle_ids)
        
        counter = Counter(all_bundle_products)
        most_common_ids = [id for id, count in counter.most_common(5)]
        return [p for p in self.products if p['id'] in most_common_ids]

# Create global recommender instance
recommender = ProductRecommender()
