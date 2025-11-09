"""
Data Collector Module
Handles data retrieval from Reddit (using PRAW) and simulates DownDetector data.
"""

import os
import random
from datetime import datetime, timedelta
import praw
from bs4 import BeautifulSoup
import requests # Used for simulated web scraping structure

class DataCollector:
    def __init__(self):
        # IMPORTANT: Replace these with your actual Reddit credentials 
        # (or leave as-is to use mock data)
        self.reddit_config = {
            'client_id': 'your_client_id', 
            'client_secret': 'your_client_secret',
            'user_agent': 'tmobile_sentiment_analyzer_v1.0 (by /u/YourRedditUsername)',
        }
        self.use_mock_data = (self.reddit_config['client_id'] == 'your_client_id')
        self.reddit = None
        
        if not self.use_mock_data:
            try:
                self.reddit = praw.Reddit(**self.reddit_config)
            except Exception as e:
                print(f"⚠️ PRAW initialization failed: {e}. Falling back to mock data.")
                self.use_mock_data = True

    def _generate_mock_posts(self, count=100):
        """Generates realistic mock posts for testing."""
        mock_issues = [
            ("5G Home Internet keeps dropping at 8 PM.", "Negative"),
            ("Data speeds tank after 20GB of usage.", "Negative"),
            ("Customer service was surprisingly helpful and fast!", "Positive"),
            ("Got a great deal on the new iPhone 16 upgrade.", "Positive"),
            ("My bill is wrong for the third month in a row.", "Negative"),
            ("Can't believe I have coverage in this remote area.", "Positive"),
            ("T-Mobile Tuesday rewards are getting worse.", "Negative"),
            ("Is the Home Internet speed affected by network congestion?", "Neutral"),
        ]
        
        posts = []
        for i in range(count):
            text, sentiment = random.choice(mock_issues)
            posts.append({
                'id': f'mock_{i}',
                'text': text + " " + " ".join([f'keyword_{j}' for j in range(random.randint(1, 3))]),
                'sentiment': sentiment, # Add a placeholder sentiment for topic labeling consistency
                'created_utc': (datetime.now() - timedelta(hours=random.randint(1, 168))).timestamp()
            })
        return posts

    def collect_reddit_posts(self, subreddits, keywords, timeframe='week', limit=1000):
        """Collects posts from specified subreddits."""
        if self.use_mock_data:
            print("   (Using mock Reddit data for demonstration. See README for API setup.)")
            return self._generate_mock_posts(500)

        print(f"   Searching {', '.join(subreddits)}...")
        posts = []
        try:
            for subreddit_name in subreddits:
                subreddit = self.reddit.subreddit(subreddit_name)
                # PRAW's search method handles keyword and time filtering efficiently
                for keyword in keywords:
                    for submission in subreddit.search(
                        query=keyword, 
                        time_filter=timeframe,
                        limit=limit // len(keywords) // len(subreddits) # Distribute limit
                    ):
                        posts.append({
                            'id': submission.id,
                            'text': submission.title + " " + submission.selftext,
                            'created_utc': submission.created_utc,
                            'subreddit': subreddit_name,
                        })
            
            # Remove duplicates based on ID
            unique_posts = {post['id']: post for post in posts}.values()
            return list(unique_posts)

        except Exception as e:
            print(f"❌ Error collecting Reddit data: {e}. Returning mock data as fallback.")
            return self._generate_mock_posts(500)

    def scrape_downdetector(self):
        """
        Simulates scraping DownDetector data to provide regional outage spikes.
        In a real scenario, this would involve a structured API or carefully managed scraping.
        """
        print("   Simulating DownDetector regional data...")
        # Define common T-Mobile issues and associated major regions
        regions = {
            "New York City": 0.15,
            "Los Angeles": 0.10,
            "Dallas": 0.05,
            "Chicago": 0.20,
            "Miami": 0.08,
            "Seattle": 0.04,
        }
        
        # Simulate a major spike in one region
        spiky_region = random.choice(list(regions.keys()))
        regional_spikes = []
        
        for region, base_level in regions.items():
            spike_intensity = base_level
            
            # If it's the spiky region, simulate a significant event
            if region == spiky_region:
                spike_intensity += random.uniform(0.3, 0.6) # Add a massive spike
            
            # Add random fluctuation
            fluctuation = random.uniform(-0.02, 0.05)
            final_intensity = max(0, min(1, spike_intensity + fluctuation))
            
            regional_spikes.append({
                'region': region,
                'outage_intensity': final_intensity, # 0.0 to 1.0 scale
                'associated_issue': "5G Home Internet outage" if region == spiky_region else "General service issues"
            })

        return regional_spikes