"""
Automated Setup Script for T-Mobile Sentiment Analyzer
Checks dependencies and helps with configuration
"""

import sys
import subprocess
import os

def check_python_version():
    """Check if Python version is 3.11+"""
    version = sys.version_info
    print(f"🐍 Python version: {version.major}.{version.minor}.{version.micro}")
    
    if version.major < 3 or (version.major == 3 and version.minor < 11):
        print("❌ ERROR: Python 3.11 or higher is required")
        print("   Please install Python 3.11+ from https://www.python.org/downloads/")
        return False
    
    print("✅ Python version is compatible")
    return True

def check_ffmpeg():
    """Check if FFmpeg is installed"""
    try:
        result = subprocess.run(['ffmpeg', '-version'], 
                              capture_output=True, 
                              text=True,
                              timeout=5)
        if result.returncode == 0:
            print("✅ FFmpeg is installed")
            return True
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass
    
    print("⚠️  FFmpeg is not installed")
    print("   Audio mixing features will not work properly")
    print("\n   Installation instructions:")
    print("   Windows: Download from https://ffmpeg.org/download.html")
    print("   Mac: Run 'brew install ffmpeg'")
    print("   Linux: Run 'sudo apt-get install ffmpeg'")
    
    response = input("\n   Continue anyway? (y/n): ")
    return response.lower() == 'y'

def install_dependencies():
    """Install Python dependencies"""
    print("\n📦 Installing Python dependencies...")
    print("   This may take 5-10 minutes for first-time setup...")
    
    try:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])
        print("✅ All dependencies installed successfully")
        return True
    except subprocess.CalledProcessError:
        print("❌ Error installing dependencies")
        print("   Try manually: pip install -r requirements.txt")
        return False

def setup_reddit_api():
    """Guide user through Reddit API setup"""
    print("\n🔧 Reddit API Configuration")
    print("   To get real Reddit data, you need API credentials")
    print("   Without them, the system will use mock data (which works fine!)")
    
    response = input("\n   Do you want to set up Reddit API now? (y/n): ")
    
    if response.lower() != 'y':
        print("   ℹ️  Skipping Reddit API setup - will use mock data")
        return
    
    print("\n   Follow these steps:")
    print("   1. Go to: https://www.reddit.com/prefs/apps")
    print("   2. Scroll to bottom and click 'Create App' or 'Create Another App'")
    print("   3. Fill in:")
    print("      - Name: T-Mobile Sentiment Analyzer")
    print("      - App type: script")
    print("      - Redirect URI: http://localhost:8080")
    print("   4. Click 'Create app'")
    print("   5. Copy the client ID (under app name) and secret")
    
    input("\n   Press Enter when you have your credentials...")
    
    client_id = input("   Enter your Client ID: ").strip()
    client_secret = input("   Enter your Client Secret: ").strip()
    
    if client_id and client_secret:
        # Update data_collector.py
        try:
            with open('data_collector.py', 'r') as f:
                content = f.read()
            
            content = content.replace(
                "client_id='your_client_id'",
                f"client_id='{client_id}'"
            )
            content = content.replace(
                "client_secret='your_client_secret'",
                f"client_secret='{client_secret}'"
            )
            
            with open('data_collector.py', 'w') as f:
                f.write(content)
            
            print("   ✅ Reddit API credentials saved!")
        except Exception as e:
            print(f"   ⚠️  Could not update credentials automatically: {e}")
            print("   Please manually edit data_collector.py")

def create_directories():
    """Create output directories"""
    directories = [
        'output/songs',
        'output/audio',
        'output/visualizations',
        'output/reports'
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
    
    print("✅ Output directories created")

def run_test():
    """Run a quick test of the system"""
    print("\n🧪 Running quick test...")
    
    try:
        # Import modules to check they work
        import praw
        import requests
        from bs4 import BeautifulSoup
        from gtts import gTTS
        import matplotlib.pyplot as plt
        
        print("✅ All modules imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("   Try reinstalling dependencies")
        return False

def main():
    """Main setup function"""
    print("=" * 60)
    print("🎵 T-MOBILE SENTIMENT ANALYZER - SETUP")
    print("=" * 60)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Check FFmpeg
    if not check_ffmpeg():
        response = input("\nAbort setup? (y/n): ")
        if response.lower() == 'y':
            sys.exit(1)
    
    # Install dependencies
    response = input("\n📦 Install Python dependencies? (y/n): ")
    if response.lower() == 'y':
        if not install_dependencies():
            sys.exit(1)
    
    # Create directories
    create_directories()
    
    # Setup Reddit API
    setup_reddit_api()
    
    # Run test
    if run_test():
        print("\n" + "=" * 60)
        print("🎉 SETUP COMPLETE!")
        print("=" * 60)
        print("\nYou're ready to go! Run the analyzer with:")
        print("   python main.py")
        print("\nFirst run will take a few minutes to download AI models.")
        print("Check README.md for detailed usage instructions.")
    else:
        print("\n⚠️  Setup completed with warnings")
        print("   Check error messages above and try running anyway")

if __name__ == "__main__":
    main()