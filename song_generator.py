"""
Song Generator Module
Generates AI songs using TTS and music combination
"""

from gtts import gTTS
from pydub import AudioSegment
from pydub.generators import Sine
import os
import random

class SongGenerator:
    def __init__(self):
        """Initialize song generator"""
        self.output_dir = 'output/songs'
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Music generation settings
        self.genres = {
            'angry': {'tempo': 180, 'instrument': 'distorted_guitar', 'style': 'rock'},
            'sad': {'tempo': 80, 'instrument': 'acoustic_guitar', 'style': 'country'},
            'happy': {'tempo': 120, 'instrument': 'pop_synth', 'style': 'pop'},
            'excited': {'tempo': 140, 'instrument': 'electronic', 'style': 'edm'}
        }
    
    def generate_song(self, topic, topic_number):
        """
        Generate AI song for a topic
        
        Args:
            topic: Topic dictionary with sentiment and examples
            topic_number: Topic index (1-5)
        
        Returns:
            Path to generated song file
        """
        print(f"      Creating lyrics...")
        
        # Generate lyrics
        lyrics = self._create_lyrics(topic)
        
        print(f"      Generating vocals...")
        
        # Create speech from lyrics
        speech_file = f"{self.output_dir}/topic_{topic_number}_speech.mp3"
        tts = gTTS(text=lyrics, lang='en', slow=False)
        tts.save(speech_file)
        
        print(f"      Composing music...")
        
        # Generate background music
        music_file = f"{self.output_dir}/topic_{topic_number}_music.mp3"
        self._create_background_music(topic, music_file)
        
        print(f"      Mixing audio...")
        
        # Mix speech with music
        output_file = f"{self.output_dir}/topic_{topic_number}_song.mp3"
        self._mix_audio(speech_file, music_file, output_file)
        
        # Clean up intermediate files
        if os.path.exists(speech_file):
            os.remove(speech_file)
        if os.path.exists(music_file):
            os.remove(music_file)
        
        print(f"      ✓ Song saved: {output_file}")
        
        return output_file
    
    def _create_lyrics(self, topic):
        """Generate lyrics based on topic and sentiment"""
        sentiment = topic['sentiment_label']
        topic_name = topic['name']
        examples = topic.get('examples', [])[:2]
        
        # Intro
        lyrics = f"This is a song about {topic_name}. "
        
        # Verse 1: Topic introduction
        if sentiment == 'Negative':
            lyrics += f"Customers are facing some challenges. "
            lyrics += f"Let me tell you what's been happening. "
        elif sentiment == 'Positive':
            lyrics += f"Customers are really loving this. "
            lyrics += f"Let me share the good news. "
        else:
            lyrics += f"There's mixed feelings about this. "
            lyrics += f"Here's what people are saying. "
        
        # Verse 2: Examples
        if examples:
            lyrics += f"One user said, {examples[0][:100]}. "
            if len(examples) > 1:
                lyrics += f"Another mentioned, {examples[1][:100]}. "
        
        # Bridge: Solution or appreciation
        if sentiment == 'Negative' and 'solution' in topic:
            solution = topic['solution']
            lyrics += f"But don't worry, there's a solution. "
            lyrics += f"{solution['title']}. "
            lyrics += f"Step one: {solution['steps'][0]['action']}. "
            lyrics += f"This will help fix the issue. "
        elif sentiment == 'Positive':
            lyrics += f"Keep up the great work T-Mobile. "
            lyrics += f"Your customers appreciate it. "
        
        # Outro
        lyrics += f"That's the story on {topic_name}. "
        lyrics += f"Stay tuned for more updates. "
        
        return lyrics
    
    def _create_background_music(self, topic, output_file):
        """Create simple background music based on mood"""
        from sentiment_analyzer import SentimentAnalyzer
        
        # Get emotion from sentiment analyzer
        analyzer = SentimentAnalyzer()
        emotion = analyzer.get_emotion_intensity(' '.join(topic.get('examples', [''])))
        
        genre_info = self.genres.get(emotion, self.genres['happy'])
        tempo = genre_info['tempo']
        
        # Create simple melody using sine waves
        # Duration: 30 seconds (matching approximate speech length)
        duration_ms = 30000
        
        # Create chord progression
        if emotion == 'angry':
            # Heavy rock progression: E5 - G5 - A5 - B5
            notes = [82.41, 98.00, 110.00, 123.47]  # E2, G2, A2, B2
        elif emotion == 'sad':
            # Minor progression: Am - F - C - G
            notes = [110.00, 87.31, 130.81, 98.00]  # A2, F2, C3, G2
        elif emotion == 'happy':
            # Major progression: C - G - Am - F
            notes = [130.81, 98.00, 110.00, 87.31]  # C3, G2, A2, F2
        else:  # excited
            # Upbeat: D - A - Bm - G
            notes = [146.83, 110.00, 123.47, 98.00]  # D3, A2, B2, G2
        
        # Generate each chord
        segments = []
        chord_duration = duration_ms // len(notes)
        
        for note in notes:
            # Create base note
            base = Sine(note).to_audio_segment(duration=chord_duration)
            # Add harmony (fifth)
            harmony = Sine(note * 1.5).to_audio_segment(duration=chord_duration)
            
            # Combine
            chord = base.overlay(harmony - 6)  # harmony quieter
            segments.append(chord)
        
        # Combine all chords
        music = sum(segments)
        
        # Reduce volume
        music = music - 20  # dB reduction
        
        # Export
        music.export(output_file, format='mp3')
    
    def _mix_audio(self, speech_file, music_file, output_file):
        """Mix speech with background music"""
        # Load files
        speech = AudioSegment.from_mp3(speech_file)
        music = AudioSegment.from_mp3(music_file)
        
        # Match lengths
        if len(speech) < len(music):
            music = music[:len(speech)]
        else:
            # Loop music if needed
            loops = (len(speech) // len(music)) + 1
            music = music * loops
            music = music[:len(speech)]
        
        # Reduce music volume to be background
        music = music - 15  # dB reduction
        
        # Overlay speech on music
        combined = music.overlay(speech)
        
        # Export
        combined.export(output_file, format='mp3')