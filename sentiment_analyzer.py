"""
Sentiment Analyzer Module
Uses Hugging Face transformers for free, pipeline-based sentiment and emotion analysis.
Requires `transformers` and `torch` dependencies.
"""

from transformers import pipeline
import random

class SentimentAnalyzer:
    def __init__(self):
        """Initialize the zero-shot sentiment and emotion classification pipelines."""
        print("   Initializing AI models for sentiment...")
        try:
            # Zero-shot classification is flexible for custom labels (Positive, Negative, Neutral)
            self.sentiment_pipe = pipeline(
                "zero-shot-classification", 
                model="typeform/mobilebert-uncased-mnli", 
                device=-1 # -1 for CPU, 0 for first GPU
            )
            # Standard model for basic emotion detection (for song genre)
            self.emotion_pipe = pipeline(
                "text-classification", 
                model="j-hartmann/emotion-english-distilroberta-base",
                top_k=4,
                device=-1
            )
            print("   ✓ AI models loaded successfully.")
        except Exception as e:
            print(f"❌ WARNING: AI model loading failed ({e}). Using mock sentiment/emotion.")
            self.sentiment_pipe = None
            self.emotion_pipe = None
            
        self.sentiment_labels = ["Positive", "Negative", "Neutral"]
        self.emotion_map = {
            'joy': 'happy', 'excitement': 'excited', 'love': 'positive',
            'anger': 'angry', 'disgust': 'angry', 'sadness': 'sad', 
            'fear': 'sad', 'surprise': 'excited'
        }

    def analyze_posts(self, posts):
        """Analyzes sentiment for a list of posts."""
        if not self.sentiment_pipe:
            # Mock sentiment if model failed to load
            for post in posts:
                post['sentiment_label'] = random.choice(self.sentiment_labels)
                post['sentiment_score'] = random.uniform(0.5, 1.0)
            print("   (Using mock sentiment analysis.)")
            return posts

        texts = [post['text'] for post in posts]
        
        # Analyze in batches to improve performance
        batch_size = 32 
        
        results = []
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            # Use multi-label=False for clean classification
            batch_results = self.sentiment_pipe(
                batch, 
                candidate_labels=self.sentiment_labels,
                multi_label=False
            )
            results.extend(batch_results)

        for post, result in zip(posts, results):
            post['sentiment_label'] = result['labels'][0]
            post['sentiment_score'] = result['scores'][0]
            
        print(f"   ✓ Analyzed sentiment for {len(posts)} posts.")
        return posts

    def get_emotion_intensity(self, text):
        """
        Determines the dominant emotion for the song genre.
        
        Args:
            text: A concatenated string of examples related to the topic.
        
        Returns:
            One of: 'angry', 'sad', 'happy', 'excited'
        """
        if not self.emotion_pipe:
            return random.choice(['angry', 'sad', 'happy', 'excited'])

        try:
            # We take the most confident prediction
            emotion_result = self.emotion_pipe(text[:512])[0][0] # Truncate for model input
            label = emotion_result['label']
            
            # Map complex labels to simplified genres
            genre = self.emotion_map.get(label, 'happy')
            return genre
        except Exception:
            # Fallback for very short or non-standard text
            return 'happy' # Default to positive if classification fails