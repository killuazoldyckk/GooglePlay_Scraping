import json
import os
from google_play_scraper import Sort, reviews
import logging
import pandas as pd
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Load the game IDs from the JSON file
game_ids_file = 'data/game_ids.json'
if not os.path.exists(game_ids_file):
    logger.error(f"Game IDs file not found: {game_ids_file}")
    exit(1)

with open(game_ids_file, 'r') as f:
    game_ids = json.load(f)

if not game_ids:
    logger.error("No game IDs found in the file.")
    exit(1)

# Function to scrape reviews for a given game ID
def scrape_reviews(game_id):
    try:
        result, continuation_token = reviews(
            game_id,
            lang='id',
            country='id',
            sort=Sort.MOST_RELEVANT,
            count=2000,
            filter_score_with=None
        )
        return result
    except Exception as e:
        logger.error(f"Error scraping reviews for game ID {game_id}: {e}")
        return []

# Custom JSON encoder to handle datetime objects
class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return json.JSONEncoder.default(self, obj)

# List to store all reviews
all_reviews = []

# Iterate through the game IDs and scrape reviews
for game_id in game_ids:
    logger.info(f"Scraping reviews for game ID: {game_id}")
    game_reviews = scrape_reviews(game_id)
    
    if not game_reviews:
        logger.warning(f"No reviews found for game ID {game_id}.")
        continue
    
    for review in game_reviews:
        review['game_id'] = game_id  # Add game ID to each review
        all_reviews.append(review)

# Convert the list of reviews to a DataFrame
reviews_df = pd.DataFrame(all_reviews)

# Save the DataFrame to a CSV file
csv_file_path = 'data/reviews/reviews.csv'
reviews_df.to_csv(csv_file_path, index=False, encoding='utf-8')
logger.info(f"Saved all reviews to {csv_file_path}")