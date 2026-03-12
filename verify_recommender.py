from models.recommender import recommender
import json

def test_semantic_search():
    print("Testing Semantic Search...")
    query = "gadgets for travel and charging"
    results, similarities = recommender.get_semantic_recommendations(query, n=2)
    
    print(f"Query: {query}")
    for p in results:
        print(f"- {p['name']} (Sim: {similarities.get(p['id']):.4f})")
    
    # Check if power bank or similar is returned
    found = any("Charger" in p['name'] or "Headphones" in p['name'] for p in results)
    print(f"Result: {'PASS' if found else 'FAIL'}")

def test_hybrid_recommendations():
    print("\nTesting Hybrid Recommendations...")
    query = "suggest a glowing skincare routine"
    user_prefs = {"favorite_categories": ["Skincare"]}
    
    results = recommender.get_hybrid_recommendations(query, user_preferences=user_prefs, n=2)
    
    print(f"Query: {query}")
    for p in results:
        print(f"- {p['name']} (${p['price']}) - Cat: {p['category']}")
        
    found_skincare = all(p['category'] == "Skincare" for p in results)
    print(f"Result (Cateogry Match): {'PASS' if found_skincare else 'FAIL'}")

if __name__ == "__main__":
    try:
        test_semantic_search()
        test_hybrid_recommendations()
    except Exception as e:
        print(f"Error during verification: {e}")
