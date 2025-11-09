"""
Topic Extractor Module
Uses scikit-learn (TF-IDF and K-Means) for topic discovery.
Generates descriptions and 4-step solutions.
"""

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from collections import Counter
import pandas as pd
import random
import re

class TopicExtractor:
    def __init__(self):
        # Stopwords tailored to telecom/social media
        self.custom_stopwords = ['tmobile', 't mobile', 'service', 'network', 'call', 'data', 'internet', 't', 'mobile', 'just', 'like', 'get', 'got', 'it', 'they', 'im']
    
    def extract_top_topics(self, analyzed_posts, downdetector_data, top_n=5):
        """
        Performs topic modeling on post text and aggregates sentiment.
        Includes DownDetector data to boost relevant topics.
        """
        if not analyzed_posts:
            print("   No posts to analyze. Returning mock topics.")
            return self._generate_mock_topics(downdetector_data, top_n)

        # 1. Prepare data
        df = pd.DataFrame(analyzed_posts)
        
        # 2. Text vectorization (TF-IDF)
        vectorizer = TfidfVectorizer(stop_words='english', min_df=5)
        try:
            X = vectorizer.fit_transform(df['text'].fillna(''))
        except ValueError:
            print("   Not enough posts for clustering. Returning mock topics.")
            return self._generate_mock_topics(downdetector_data, top_n)

        # 3. K-Means Clustering (Topic Modeling)
        # Use more clusters than needed to ensure good separation
        num_clusters = min(25, len(df)//50) 
        if num_clusters < top_n: num_clusters = top_n + 5

        kmeans = KMeans(n_clusters=num_clusters, random_state=42, n_init=10, max_iter=300)
        df['cluster'] = kmeans.fit_predict(X)
        
        # 4. Analyze clusters
        topics = []
        order_by_score = []

        for i in range(num_clusters):
            cluster_df = df[df['cluster'] == i]
            if len(cluster_df) < 20: continue # Ignore very small clusters

            # Get top keywords
            feature_names = vectorizer.get_feature_names_out()
            cluster_center = kmeans.cluster_centers_[i]
            top_feature_indices = cluster_center.argsort()[-10:][::-1]
            keywords = [feature_names[j] for j in top_feature_indices]
            
            # Aggregate sentiment
            sentiment_counts = cluster_df['sentiment_label'].value_counts(normalize=True)
            dominant_sentiment = sentiment_counts.idxmax()
            avg_score = cluster_df['sentiment_score'].mean()
            
            topic_name = " ".join(keywords[:3]).title()

            topic_data = {
                'id': i,
                'name': topic_name,
                'keywords': keywords,
                'count': len(cluster_df),
                'sentiment_label': dominant_sentiment,
                'sentiment_score': avg_score,
                'examples': cluster_df['text'].sample(min(10, len(cluster_df))).tolist(),
                'regional_boost': 0 # Will be updated
            }
            topics.append(topic_data)
        
        # 5. Apply DownDetector Boost
        self._apply_downdetector_boost(topics, downdetector_data)
        
        # 6. Rank and finalize top N topics
        # Score = Count * (Sentiment_Confidence + Regional_Boost)
        for topic in topics:
            score = topic['count'] * (topic['sentiment_score'] + topic['regional_boost'])
            order_by_score.append((score, topic))
            
        final_topics = [t for score, t in sorted(order_by_score, key=lambda x: x[0], reverse=True)[:top_n]]
        
        # 7. Generate descriptions and solutions for final topics
        for topic in final_topics:
            topic['description'] = self._generate_description(topic)
            if topic['sentiment_label'] == 'Negative':
                topic['solution'] = self._generate_solution(topic)
            elif topic['sentiment_label'] == 'Positive':
                topic['solution'] = self._generate_positive_action(topic)
        
        return final_topics
    
    def _apply_downdetector_boost(self, topics, downdetector_data):
        """Boosts topics related to regional outages."""
        regional_keywords = ['outage', 'slow', 'drop', 'speed', 'internet', '5g', 'home']
        
        total_intensity = sum(r['outage_intensity'] for r in downdetector_data)
        if total_intensity == 0:
            return

        for topic in topics:
            boost_factor = 0
            # Check if topic keywords overlap with regional keywords
            for keyword in topic['keywords']:
                if keyword in regional_keywords:
                    boost_factor += 0.2
            
            # Apply boost proportional to overall outage intensity
            topic['regional_boost'] = min(0.5, boost_factor * total_intensity)

    def _generate_description(self, topic):
        """Creates a narrative description of the topic."""
        sentiment_word = {
            'Positive': 'great, customers are thrilled with',
            'Negative': 'concerning, users are consistently complaining about',
            'Neutral': 'mixed, the community is debating the topic of'
        }.get(topic['sentiment_label'], 'neutral')
        
        core_keywords = ', '.join(topic['keywords'][:4])
        
        desc = f"This is a {sentiment_word} issue related to **{topic['name']}**. "
        desc += f"It has been mentioned {topic['count']} times in recent posts. "
        desc += f"The core focus of this discussion involves key terms like: {core_keywords}. "
        
        if topic.get('regional_boost', 0) > 0.1:
            desc += "This topic is significantly amplified by current regional service interruptions."

        return desc

    def _generate_solution(self, topic):
        """Generates a hardcoded 4-step solution for negative topics."""
        title_map = {
            '5G Home Internet': 'Troubleshooting 5G Home Internet Drops',
            'customer service': 'How to Escalate Customer Service Issues',
            'billing': 'Fixing Recurring Billing Errors',
            'upgrade': 'Handling Failed Upgrade/Trade-in Processes',
            'data speed': 'Optimizing Throttled Data Speeds',
        }
        
        # Determine the primary focus to select a solution
        focus = next((k for k in title_map if k in topic['name']), 'data speed')
        
        # Hardcoded solutions based on common T-Mobile issues (as per project request)
        if focus == '5G Home Internet':
            solution = {
                'title': "Optimize Your 5G Home Internet Router Placement",
                'steps': [
                    {'action': 'Perform a Signal Scan for Optimal Placement', 
                     'fixes': 'Poor indoor signal penetration and device drops.', 
                     'how': 'Move the gateway around your home, checking the signal strength on the app. Place it near a window, away from metal objects and major appliances.'},
                    {'action': 'Check for the Latest Firmware Update', 
                     'fixes': 'Known bugs and intermittent connection issues.', 
                     'how': 'Use the T-Mobile Internet app to check the gateway status. If an update is available, follow prompts to install it (often requires a reboot).'},
                    {'action': 'Split Wi-Fi Bands (2.4GHz and 5GHz)', 
                     'fixes': 'Device compatibility and slow speeds on crowded bands.', 
                     'how': 'Access the gateway settings (usually 192.168.1.1 or the app) and disable Smart Steering to give the 2.4GHz and 5GHz bands separate names.'},
                    {'action': 'Power Cycle and Check Cooling', 
                     'fixes': 'Overheating and general performance degradation.', 
                     'how': 'Unplug the power cord for 30 seconds, then plug it back in. Ensure the device is in a well-ventilated area and not enclosed.'},
                ]
            }
        elif focus == 'customer service':
             solution = {
                'title': "Escalate Effectively: Contacting the T-Force Team",
                'steps': [
                    {'action': 'Document Everything Before Contacting', 
                     'fixes': 'Inconsistent information and repeating yourself to new agents.', 
                     'how': 'Record dates, times, agent names, and ticket numbers for all prior interactions.'},
                    {'action': 'Contact T-Force via Twitter or Facebook', 
                     'fixes': 'Getting stuck in automated phone loops and standard tier support.', 
                     'how': 'Send a private message to @TMobileHelp on Twitter or T-Mobile’s Facebook page. This team is US-based and often handles escalations faster.'},
                    {'action': 'Request a Supervisor Callback or Ticket Review', 
                     'fixes': 'Unresolved issues handled by Tier 1 support.', 
                     'how': 'Politely ask the T-Force agent to flag your case for a Tier 2 specialist or supervisor review with a specific resolution requested.'},
                    {'action': 'File an FCC Complaint if Necessary', 
                     'fixes': 'Long-standing, systemic billing or service issues that T-Mobile has failed to fix.', 
                     'how': 'Submit a complaint on the FCC website. T-Mobile executive support often contacts the customer directly within a few business days.'},
                ]
            }
        else: # Default for 'data speed', 'billing', 'upgrade', or unknown
            solution = {
                'title': "General Network Optimization and Data Check",
                'steps': [
                    {'action': 'Check Network Status and APN Settings', 
                     'fixes': 'Local tower maintenance or incorrect phone configuration.', 
                     'how': 'Use the T-Mobile app or DownDetector to check local outages. Verify your APN is set to "fast.t-mobile.com".'},
                    {'action': 'Reboot and Reset Network Settings', 
                     'fixes': 'Temporary glitches or corrupted network cache on your device.', 
                     'how': 'Toggle Airplane Mode on and off, then if that fails, go to device settings and select "Reset Network Settings" (Note: this deletes saved Wi-Fi passwords).'},
                    {'action': 'Verify Data Throttling Status', 
                     'fixes': 'Slow speeds due to reaching your high-speed data cap.', 
                     'how': 'Check your plan details on the T-Mobile app to see if you have exceeded your premium data allowance for the month.'},
                    {'action': 'Secure a T-Mobile Network Pass', 
                     'fixes': 'Connectivity issues when traveling or roaming.', 
                     'how': 'If you are experiencing issues on a partner network, purchase a T-Mobile Network Pass to switch to the nearest preferred network.'},
                ]
            }
        return solution

    def _generate_positive_action(self, topic):
        """Generates an action based on positive trends (what customers would enjoy)."""
        
        # Hardcoded positive actions based on common T-Mobile positive feedback
        positive_actions = {
            'T-Mobile Tuesday': {
                'title': 'Maximize Your T-Mobile Tuesday Rewards',
                'description': 'Since customers love the Tuesday rewards, here is how to get the most out of them.',
                'steps': [
                    {'action': 'Set Weekly Reminders', 'fixes': 'Missing out on limited-time, high-value deals.', 'how': 'Configure a weekly alert on your phone for every Tuesday morning to check the T-Mobile Tuesdays app.'},
                    {'action': 'Stack Free Products/Services', 'fixes': 'Not getting full value when multiple offers are available.', 'how': 'Check for codes (like free Dunkin’ or Shell gas) that can be used immediately and stack them with partner services (like Apple TV+ or Netflix on Us).'},
                    {'action': 'Share Unwanted Codes with Family', 'fixes': 'Letting valuable coupon codes expire without use.', 'how': 'Send codes for services you don’t need (e.g., movie tickets or discount codes) to friends or family members who will use them before expiry.'},
                    {'action': 'Check Partner Promotions in the App', 'fixes': 'Only focusing on the main Tuesday deal and missing other partner benefits.', 'how': 'Regularly scroll through the "Partners" section in the app for ongoing, non-Tuesday benefits like travel and shopping discounts.'},
                ]
            },
            'Customer Service': {
                'title': 'How to Get Fast, Excellent Customer Service',
                'description': 'Customers praised the fast resolution, here is how to achieve it consistently.',
                'steps': [
                     {'action': 'Use the T-Force Channels', 'fixes': 'Slow resolution times through the standard phone line.', 'how': 'Engage with T-Mobile support via Twitter (@TMobileHelp) or Facebook messenger. These teams are typically more empowered and faster.'},
                     {'action': 'Use the App Chat for Quick Questions', 'fixes': 'Overcomplicating simple questions that don’t require a phone call.', 'how': 'For account questions or basic troubleshooting, use the integrated chat feature in the T-Mobile app for near-instant responses.'},
                     {'action': 'Prepare Account Details in Advance', 'fixes': 'Wasting time at the start of the call verifying your identity.', 'how': 'Have your PIN and account number ready before connecting with an agent or starting a chat.'},
                     {'action': 'Be Clear and Concise with the Problem', 'fixes': 'Misunderstanding or slow resolution due to vague problem descriptions.', 'how': 'Start the interaction with a single, clear sentence summarizing the issue and what resolution you expect.'},
                ]
            },
        }

        # Select action based on primary positive focus
        focus = next((k for k in positive_actions if k in topic['name']), 'T-Mobile Tuesday')
        return positive_actions[focus]


    def _generate_mock_topics(self, downdetector_data, top_n=5):
        """Generates mock topics for error fallback."""
        mock_topics = [
            {'name': 'Slow 5G Home Internet', 'sentiment_label': 'Negative', 'sentiment_score': 0.85, 'count': 250, 'regional_boost': 0.3, 'keywords': ['slow', 'drops', 'disconnect', '5g'], 'examples': ["The internet keeps dropping every night.", "Super slow speeds in the evening."], 'solution': self._generate_solution({'name': '5G Home Internet'}, True)},
            {'name': 'Excellent Customer Service', 'sentiment_label': 'Positive', 'sentiment_score': 0.92, 'count': 180, 'regional_boost': 0.0, 'keywords': ['rep', 'fast', 'solved', 'helpful'], 'examples': ["The agent solved my issue in minutes!", "Best customer service I've had in years."], 'solution': self._generate_positive_action({'name': 'Customer Service'})},
            {'name': 'T-Mobile Tuesday Rewards', 'sentiment_label': 'Positive', 'sentiment_score': 0.78, 'count': 150, 'regional_boost': 0.0, 'keywords': ['free', 'deals', 'tuesday', 'thanks'], 'examples': ["Another free coffee thanks to T-Mobile Tuesday!", "Love the new rewards partners."], 'solution': self._generate_positive_action({'name': 'T-Mobile Tuesday'})},
            {'name': 'Billing Error Issues', 'sentiment_label': 'Negative', 'sentiment_score': 0.75, 'count': 120, 'regional_boost': 0.1, 'keywords': ['bill', 'wrong', 'overcharge', 'credit'], 'examples': ["My bill is wrong again.", "I was overcharged by $50 this month."], 'solution': self._generate_solution({'name': 'billing'}, True)},
            {'name': 'New Phone Upgrade Deals', 'sentiment_label': 'Neutral', 'sentiment_score': 0.55, 'count': 100, 'regional_boost': 0.0, 'keywords': ['iphone', 'samsung', 'tradein', 'promo'], 'examples': ["Is this a good deal on the new iPhone?", "The trade-in values are kind of low."], 'solution': None},
        ]
        # Generate descriptions using the internal method
        for topic in mock_topics:
            topic['description'] = self._generate_description(topic)
        
        return mock_topics[:top_n]