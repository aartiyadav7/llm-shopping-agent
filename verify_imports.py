import sys
import os

# Add the project directory to sys.path
project_dir = os.path.join(os.getcwd(), "AI Shopping Agent")
sys.path.append(project_dir)

try:
    from models.recommender import recommender
    print("Successfully imported recommender")
    print(f"Number of products loaded: {len(recommender.products)}")
except Exception as e:
    print(f"Failed to import: {e}")
    sys.exit(1)
