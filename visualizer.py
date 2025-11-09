"""
Data Visualizer Module
Generates Matplotlib and Seaborn charts for the final report.
"""

import os
import random
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

class DataVisualizer:
    def __init__(self):
        self.output_dir = 'output/visualizations'
        os.makedirs(self.output_dir, exist_ok=True)

    def create_topic_charts(self, hot_topics):
        """Creates a bar chart showing topic frequency and color-coded by sentiment."""
        df = pd.DataFrame(hot_topics)
        
        # Define colors for sentiment
        sentiment_colors = {
            'Positive': '#00C853',  # Green
            'Negative': '#D32F2F',  # Red
            'Neutral': '#FFA000'    # Amber
        }
        colors = [sentiment_colors[s] for s in df['sentiment_label']]

        plt.figure(figsize=(10, 6))
        
        # Sort by count for better visualization
        df_sorted = df.sort_values(by='count', ascending=False)

        sns.barplot(
            x='count', 
            y='name', 
            data=df_sorted, 
            palette=colors,
            orient='h'
        )
        
        plt.title('Top 5 T-Mobile Hot Topics by Mention Count (Sentiment Color-Coded)', fontsize=14)
        plt.xlabel('Total Mentions (Count)', fontsize=12)
        plt.ylabel('Topic Name', fontsize=12)
        plt.grid(axis='x', linestyle='--', alpha=0.6)
        plt.tight_layout()
        
        chart_path = f"{self.output_dir}/topic_bar_chart.png"
        plt.savefig(chart_path)
        plt.close()
        print(f"   ✓ Topic bar chart saved: {chart_path}")
        return chart_path

    def create_sentiment_heatmap(self, analyzed_posts, downdetector_data):
        """
        Creates a mock regional sentiment heatmap merged with DownDetector data.
        Since Reddit posts often lack explicit region, this is a simulated merge
        for visualization purposes.
        """
        
        # 1. Create Mock Regional Sentiment (since actual geo-tagging is hard/expensive)
        # Assign a random region to each post for the purpose of the demo
        regions = [r['region'] for r in downdetector_data]
        if not regions: regions = ['Global']
        
        # Map sentiment labels to a numerical score for aggregation
        sentiment_map = {'Positive': 1, 'Negative': -1, 'Neutral': 0}

        regional_sentiment = {region: {'score': 0, 'count': 0} for region in regions}
        
        for post in analyzed_posts:
            # Randomly assign a region for mock purposes
            region = random.choice(regions)
            score = sentiment_map.get(post.get('sentiment_label'), 0)
            regional_sentiment[region]['score'] += score
            regional_sentiment[region]['count'] += 1

        # Calculate average sentiment (between -1 and 1)
        for region in regional_sentiment:
            if regional_sentiment[region]['count'] > 0:
                regional_sentiment[region]['avg_sentiment'] = regional_sentiment[region]['score'] / regional_sentiment[region]['count']
            else:
                regional_sentiment[region]['avg_sentiment'] = 0.0

        # 2. Merge with DownDetector data
        regional_df = pd.DataFrame(regional_sentiment).T.reset_index().rename(columns={'index': 'Region'})
        dd_df = pd.DataFrame(downdetector_data)
        dd_df = dd_df.rename(columns={'region': 'Region', 'outage_intensity': 'Outage Intensity'})
        
        # Merge by region
        merged_df = pd.merge(regional_df, dd_df, on='Region', how='outer').fillna(0)
        
        # Create a combined metric for the heatmap (e.g., Sentiment vs. Outage)
        heatmap_data = merged_df[['Region', 'avg_sentiment', 'Outage Intensity']]
        heatmap_data = heatmap_data.set_index('Region')

        plt.figure(figsize=(8, 6))
        # Use a diverging color map (Red for low sentiment/high outage, Green for high sentiment/low outage)
        sns.heatmap(
            heatmap_data, 
            annot=True, 
            cmap='RdYlGn', 
            fmt=".2f",
            linewidths=.5, 
            linecolor='lightgray',
            cbar_kws={'label': 'Metric Value'}
        )
        
        plt.title('Regional Sentiment & Outage Intensity', fontsize=14)
        plt.yticks(rotation=0)
        plt.tight_layout()

        chart_path = f"{self.output_dir}/regional_heatmap.png"
        plt.savefig(chart_path)
        plt.close()
        print(f"   ✓ Regional heatmap saved: {chart_path}")
        return chart_path