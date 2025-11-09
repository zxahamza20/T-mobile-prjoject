🎵 T-Mobile Pulse: Social Sentiment Analyzer & AI Song Generator

Welcome to T-Mobile Pulse, an innovative project that combines social media data analysis, AI-driven topic modeling, accessibility features, and a unique personality through AI-generated music.

This application collects T-Mobile-related discussions from Reddit, analyzes sentiment, extracts the top 5 trending topics, generates actionable solutions, and composes a 30-second song for each topic based on its emotional tone.

🚀 Project Components

File

Role

Technologies Used

main.py

Application Entry Point, Orchestrates the Pipeline

Python 3.11

data_collector.py

Fetches Reddit data (via PRAW) and simulates DownDetector data.

praw, requests, Mocking

sentiment_analyzer.py

Analyzes text sentiment and emotion using free AI models.

transformers (Hugging Face)

topic_extractor.py

Discovers top topics (K-Means/TF-IDF) and generates 4-step solutions.

scikit-learn, pandas

song_generator.py

Creates lyrics (based on topic), generates vocals (gTTS), and composes background music (pydub sine waves), then mixes them.

gTTS, pydub

voice_narrator.py

Generates welcome and topic summary audio for accessibility (ADS-friendly).

gTTS

visualizer.py

Generates charts (topic bars, regional heatmap) for the HTML report.

matplotlib, seaborn

setup.py

Automated script to check environment and install dependencies.

subprocess

🛠️ Setup Instructions

Prerequisites

Python 3.11+: This project requires Python version 3.11 or newer.

FFmpeg: Required by the pydub library to handle audio file mixing and exporting (.mp3 generation).

Mac (Homebrew): brew install ffmpeg

Windows: Download the installer and ensure the bin folder is added to your system PATH.

Linux (Ubuntu/Debian): sudo apt install ffmpeg

Step 1: Install Python Dependencies

Run the included setup script to check prerequisites and install the necessary libraries listed in requirements.txt:

python setup.py


If the setup script fails, you can manually install the dependencies:

pip install -r requirements.txt


Step 2: Configure Reddit API (Optional)

The data_collector.py file is currently set to use mock data to ensure the entire application runs out of the box (as you requested a no-cost solution).

To use real-time Reddit data, you must configure a PRAW application:

Go to Reddit's App Preferences.

Click "Create an app..."

Choose "script" and set the Redirect URI to http://localhost:8080.

Copy the Client ID (under the app name) and the Client Secret (the secret string).

Edit data_collector.py and replace the placeholders:

self.reddit_config = {
    'client_id': 'YOUR_CLIENT_ID_HERE', 
    'client_secret': 'YOUR_CLIENT_SECRET_HERE',
    # ...
}


🏃 Running the Analyzer

Run the main application entry point and follow the on-screen prompts:

python main.py


The script will:

Collect data (or mock data).

Run AI sentiment analysis.

Extract top 5 topics and generate solutions.

Generate charts in the output/visualizations folder.

Generate the 30-second AI songs in the output/songs folder.

Generate accessibility audio in the output/audio folder.

Generate a final comprehensive HTML report in the output/reports folder.

Provide an interactive console menu for testing the generated audio files.