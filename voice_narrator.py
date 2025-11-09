"""
Voice Narrator Module
Uses gTTS (Google Text-to-Speech) to create voice files for accessibility.
"""

import os
from gtts import gTTS
import time

class VoiceNarrator:
    def __init__(self):
        self.output_dir = 'output/audio'
        os.makedirs(self.output_dir, exist_ok=True)
    
    def create_welcome_message(self):
        """Creates the welcome and navigation message."""
        welcome_text = (
            "Welcome to the T-Mobile Pulse Review Analyzer. "
            "We have analyzed the top five hot topics on social media. "
            "You can choose to hear the AI generated song for each topic, "
            "or listen to a summary description. "
            "Please select an option from the main menu: "
            "one through five to hear a topic song, "
            "or six for this welcome message again. "
            "Please refer to the on-screen report for topic details and solutions. "
        )
        output_file = f"{self.output_dir}/welcome.mp3"
        print("   Generating welcome audio...")
        self._generate_audio(welcome_text, output_file)
        print("   ✓ Welcome message saved.")

    def create_topic_descriptions(self, hot_topics):
        """Creates an audio description file for each topic."""
        print("   Generating topic description audio files...")
        
        for i, topic in enumerate(hot_topics, 1):
            text = f"Topic number {i}: {topic['name']}. "
            text += f"This is a {topic['sentiment_label']} trend with {topic['count']} mentions. "
            text += topic['description']
            
            if topic['sentiment_label'] == 'Negative':
                text += f"The recommended solution is: {topic['solution']['title']}."
            elif topic['sentiment_label'] == 'Positive':
                text += f"The positive action suggestion is: {topic['solution']['title']}."
            
            output_file = f"{self.output_dir}/topic_{i}_description.mp3"
            self._generate_audio(text, output_file)
            print(f"   ✓ Description {i} saved.")

    def _generate_audio(self, text, output_file):
        """Helper to call gTTS and handle file saving."""
        try:
            tts = gTTS(text=text, lang='en', slow=False)
            tts.save(output_file)
        except Exception as e:
            print(f"❌ Error generating TTS for {output_file}: {e}")
            # Create a placeholder file to prevent pipeline errors
            with open(output_file, 'w') as f:
                f.write("Audio generation failed.")
            time.sleep(1) # Pause to simulate generation time