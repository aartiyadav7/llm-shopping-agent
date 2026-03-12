import os
import requests
from typing import List, Dict

def fetch_external_prices(product_name: str) -> List[Dict]:
    """
    Simulates fetching real-time prices from various sites.
    In a real-world scenario, this would use a SerpApi, Scraper, or official APIs.
    """
    # Simulate some variation in pricing
    base_prices = {
        "Amazon": 0.95,  # 5% cheaper than MSRP
        "Best Buy": 1.0, # MSRP
        "Walmart": 0.98, # 2% cheaper
        "eBay": 0.85     # 15% cheaper (refurbished/used)
    }
    
    # In this project, we'll simulate the "live" results
    # To make it realer for the user, we could use a search tool if available,
    # but since we want to demonstrate the engine logic:
    
    results = []
    # Using a dummy MSRP of 100 for simulation if product not found in local db
    msrp = 100.0 
    
    # Try to find the local price for better simulation
    from models.recommender import recommender
    search_results = recommender.get_hybrid_recommendations(product_name, n=1)
    if search_results:
        msrp = search_results[0]['price']

    for site, multiplier in base_prices.items():
        price = round(msrp * multiplier, 2)
        results.append({
            "site": site,
            "price": price,
            "url": f"https://www.{site.lower().replace(' ', '')}.com/search?q={product_name.replace(' ', '+')}",
            "currency": "$"
        })
    
    # Sort by price (cheapest to heavy)
    results.sort(key=lambda x: x['price'])
    
    return results
