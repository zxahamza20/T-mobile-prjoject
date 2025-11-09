"""
T-Mobile Social Media Sentiment Analysis & AI Song Generator
Main application entry point
Python 3.11
"""

import os
import sys
from datetime import datetime, timedelta
from data_collector import DataCollector
from sentiment_analyzer import SentimentAnalyzer
from topic_extractor import TopicExtractor
from song_generator import SongGenerator
from voice_narrator import VoiceNarrator
from visualizer import DataVisualizer

class TMobileAnalyzer:
    def __init__(self):
        self.data_collector = DataCollector()
        self.sentiment_analyzer = SentimentAnalyzer()
        self.topic_extractor = TopicExtractor()
        self.song_generator = SongGenerator()
        self.narrator = VoiceNarrator()
        self.visualizer = DataVisualizer()
        
        # Create output directories
        os.makedirs('output/songs', exist_ok=True)
        os.makedirs('output/audio', exist_ok=True)
        os.makedirs('output/visualizations', exist_ok=True)
        os.makedirs('output/reports', exist_ok=True)
    
    def run_analysis(self, timeframe='week'):
        """Run complete analysis pipeline"""
        print("=" * 60)
        print("T-MOBILE SOCIAL SENTIMENT ANALYZER")
        print("=" * 60)
        
        # Step 1: Collect data
        print("\n[1/6] Collecting social media data...")
        posts = self.data_collector.collect_reddit_posts(
            subreddits=['tmobile', 'cellphones', 'NoContract'],
            keywords=['t-mobile', 'tmobile', 't mobile'],
            timeframe=timeframe
        )
        
        downdetector_data = self.data_collector.scrape_downdetector()
        
        print(f"   ✓ Collected {len(posts)} posts")
        print(f"   ✓ Retrieved DownDetector data for {len(downdetector_data)} regions")
        
        # Step 2: Analyze sentiment
        print("\n[2/6] Analyzing sentiment...")
        analyzed_posts = self.sentiment_analyzer.analyze_posts(posts)
        
        # Step 3: Extract hot topics
        print("\n[3/6] Extracting hot topics...")
        hot_topics = self.topic_extractor.extract_top_topics(
            analyzed_posts, 
            downdetector_data,
            top_n=5
        )
        
        for i, topic in enumerate(hot_topics, 1):
            print(f"   Topic {i}: {topic['name']} ({topic['sentiment_label']}) - {topic['count']} mentions")
        
        # Step 4: Generate visualizations
        print("\n[4/6] Creating visualizations...")
        self.visualizer.create_topic_charts(hot_topics)
        self.visualizer.create_sentiment_heatmap(analyzed_posts, downdetector_data)
        
        # Step 5: Generate AI songs
        print("\n[5/6] Generating AI songs for each topic...")
        song_files = []
        for i, topic in enumerate(hot_topics, 1):
            print(f"   Generating song {i}/5: {topic['name']}...")
            song_path = self.song_generator.generate_song(topic, i)
            song_files.append(song_path)
            topic['song_file'] = song_path
        
        # Step 6: Create navigation audio
        print("\n[6/6] Creating voice navigation system...")
        self.narrator.create_welcome_message()
        self.narrator.create_topic_descriptions(hot_topics)
        
        # Generate final report
        self.generate_report(hot_topics)
        
        print("\n" + "=" * 60)
        print("ANALYSIS COMPLETE!")
        print("=" * 60)
        print(f"\nOutput files saved to:")
        print(f"  - Songs: output/songs/")
        print(f"  - Audio: output/audio/")
        print(f"  - Visualizations: output/visualizations/")
        print(f"  - Reports: output/reports/")
        
        return hot_topics
    
    def generate_report(self, hot_topics):
        """Generate comprehensive HTML report"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_path = f"output/reports/tmobile_analysis_{timestamp}.html"
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>T-Mobile Sentiment Analysis Report</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }}
                .header {{ background: #e20074; color: white; padding: 20px; border-radius: 10px; }}
                .topic {{ background: white; margin: 20px 0; padding: 20px; border-radius: 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }}
                .positive {{ border-left: 5px solid #00c853; }}
                .negative {{ border-left: 5px solid #d32f2f; }}
                .neutral {{ border-left: 5px solid #ffa000; }}
                .solution {{ background: #e3f2fd; padding: 15px; margin: 10px 0; border-radius: 5px; }}
                audio {{ width: 100%; margin: 10px 0; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>🎵 T-Mobile Social Sentiment Analysis</h1>
                <p>Generated: {datetime.now().strftime("%B %d, %Y at %I:%M %p")}</p>
            </div>
        """
        
        for i, topic in enumerate(hot_topics, 1):
            sentiment_class = topic['sentiment_label'].lower()
            
            html += f"""
            <div class="topic {sentiment_class}">
                <h2>Topic {i}: {topic['name']}</h2>
                <p><strong>Sentiment:</strong> {topic['sentiment_label']} ({topic['sentiment_score']:.2f})</p>
                <p><strong>Mentions:</strong> {topic['count']}</p>
                <p><strong>Description:</strong> {topic['description']}</p>
                
                <h3>🎵 AI Generated Song</h3>
                <audio controls>
                    <source src="../songs/topic_{i}_song.mp3" type="audio/mpeg">
                </audio>
                
                <h3>Example Posts:</h3>
                <ul>
            """
            
            for example in topic['examples'][:3]:
                html += f"<li>{example}</li>"
            
            html += "</ul>"
            
            if topic['sentiment_label'] == 'Negative':
                html += f"""
                <div class="solution">
                    <h3>💡 Recommended Solution</h3>
                    <p><strong>{topic['solution']['title']}</strong></p>
                    <ol>
                """
                for step in topic['solution']['steps']:
                    html += f"""
                    <li>
                        <strong>{step['action']}</strong><br>
                        <em>Fixes:</em> {step['fixes']}<br>
                        <em>How:</em> {step['how']}
                    </li>
                    """
                html += "</ol></div>"
            
            html += "</div>"
        
        html += """
        </body>
        </html>
        """
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(html)
        
        print(f"   ✓ Report generated: {report_path}")

def main():
    """Main entry point"""
    analyzer = TMobileAnalyzer()
    
    print("\nSelect timeframe:")
    print("1. Today")
    print("2. This Week")
    print("3. This Month")
    
    choice = input("\nEnter choice (1-3) [default: 2]: ").strip()
    
    timeframe_map = {
        '1': 'day',
        '2': 'week',
        '3': 'month',
        '': 'week'
    }
    
    timeframe = timeframe_map.get(choice, 'week')
    
    try:
        hot_topics = analyzer.run_analysis(timeframe)
        
        # Interactive navigation
        print("\n" + "=" * 60)
        print("INTERACTIVE NAVIGATION")
        print("=" * 60)
        
        while True:
            print("\nOptions:")
            print("1-5: Play song for topic 1-5")
            print("6: Play welcome message")
            print("7: Exit")
            
            choice = input("\nEnter choice: ").strip()
            
            if choice in ['1', '2', '3', '4', '5']:
                topic_num = int(choice)
                if topic_num <= len(hot_topics):
                    topic = hot_topics[topic_num - 1]
                    print(f"\nPlaying: {topic['name']}")
                    print(f"File: {topic['song_file']}")
                    # In a real implementation, you'd use pygame or similar to play audio
                    print("(Audio playback would happen here)")
            elif choice == '6':
                print("\nPlaying welcome message...")
                print("File: output/audio/welcome.mp3")
            elif choice == '7':
                print("\nThank you for using T-Mobile Sentiment Analyzer!")
                break
            else:
                print("Invalid choice. Please try again.")
    
    except KeyboardInterrupt:
        print("\n\nAnalysis interrupted by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()