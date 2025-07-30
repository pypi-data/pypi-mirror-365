"""
Speech capabilities examples for LangChain DeepAI integration.

This script demonstrates text-to-speech and speech-to-text capabilities.
"""

import os
from langchain_deepai import TextToSpeechDeepAI, SpeechToTextDeepAI

def text_to_speech_example():
    """Text-to-speech generation example."""
    print("=== Text-to-Speech Example ===")
    
    # Initialize TTS client
    tts = TextToSpeechDeepAI()
    
    # Convert text to speech
    text = "Hello! This is a demonstration of DeepAI's text-to-speech capabilities integrated with LangChain."
    
    result = tts.synthesize(
        text=text,
        voice="default"
    )
    
    # Save audio file
    with open("demo_speech.wav", "wb") as f:
        f.write(result["audio_data"])
    
    print(f"Speech generated and saved to: demo_speech.wav")
    print(f"Audio URL: {result['audio_url']}")
    print(f"Text length: {result['metadata']['text_length']} characters")
    print(f"Voice used: {result['metadata']['voice']}")


def different_voices_example():
    """Example using different voices."""
    print("\n=== Different Voices Example ===")
    
    tts = TextToSpeechDeepAI()
    
    # Get available voices
    voices = tts.get_available_voices()
    print("Available voices:")
    for voice_name, info in voices.items():
        print(f"  {voice_name}: {info['description']} ({info['gender']})")
    
    # Generate speech with different voices
    text = "This is a test of different voice options."
    
    for voice_name in ["default", "female", "male"]:
        try:
            result = tts.synthesize_and_save(
                text=text,
                filepath=f"voice_{voice_name}.wav",
                voice=voice_name
            )
            print(f"✓ Generated speech with {voice_name} voice")
        except Exception as e:
            print(f"✗ Failed with {voice_name} voice: {e}")


def batch_tts_example():
    """Example of batch text-to-speech processing."""
    print("\n=== Batch TTS Example ===")
    
    tts = TextToSpeechDeepAI()
    
    texts = [
        "Welcome to our service.",
        "Please follow the instructions carefully.",
        "Thank you for using our application.",
        "Have a great day!"
    ]
    
    print(f"Converting {len(texts)} texts to speech...")
    results = tts.synthesize_multiple(texts, voice="default")
    
    for i, result in enumerate(results):
        if "error" not in result:
            filename = f"batch_speech_{i+1}.wav"
            with open(filename, "wb") as f:
                f.write(result["audio_data"])
            print(f"✓ Speech {i+1} saved to: {filename}")
        else:
            print(f"✗ Speech {i+1} failed: {result['error']}")


def speech_to_text_example():
    """Speech-to-text transcription example."""
    print("\n=== Speech-to-Text Example ===")
    
    # Initialize STT client
    stt = SpeechToTextDeepAI()
    
    # Note: You need an actual audio file for this to work
    # This is a demonstration of how to use it
    audio_file = "demo_speech.wav"  # Generated from previous example
    
    if os.path.exists(audio_file):
        try:
            result = stt.transcribe(audio_file, language="auto")
            print(f"Transcribed text: {result['text']}")
            print(f"Language: {result['language']}")
            print(f"Metadata: {result['metadata']}")
        except Exception as e:
            print(f"Transcription failed: {e}")
    else:
        print(f"Audio file {audio_file} not found. Run TTS example first.")


def batch_stt_example():
    """Example of batch speech-to-text processing."""
    print("\n=== Batch STT Example ===")
    
    stt = SpeechToTextDeepAI()
    
    # List of audio files to transcribe
    audio_files = [
        "voice_default.wav",
        "voice_female.wav", 
        "voice_male.wav"
    ]
    
    # Filter to only existing files
    existing_files = [f for f in audio_files if os.path.exists(f)]
    
    if existing_files:
        print(f"Transcribing {len(existing_files)} audio files...")
        results = stt.transcribe_multiple(existing_files, language="auto")
        
        for i, result in enumerate(results):
            if "error" not in result:
                print(f"✓ File {i+1}: {result['text']}")
            else:
                print(f"✗ File {i+1} failed: {result['error']}")
    else:
        print("No audio files found. Run TTS examples first.")


def audio_file_info_example():
    """Example showing audio file information."""
    print("\n=== Audio File Information ===")
    
    stt = SpeechToTextDeepAI()
    
    # Check supported formats
    formats = stt.get_supported_formats()
    print("Supported audio formats:")
    for format_name, info in formats.items():
        print(f"  {format_name}: {info['description']} - {info['recommended_for']}")
    
    # Check supported languages
    languages = stt.get_supported_languages()
    print("\nSupported languages:")
    for lang_code, lang_name in languages.items():
        print(f"  {lang_code}: {lang_name}")
    
    # Get file info for existing audio files
    audio_files = ["demo_speech.wav", "voice_default.wav"]
    for audio_file in audio_files:
        if os.path.exists(audio_file):
            try:
                file_info = stt.get_file_info(audio_file)
                print(f"\nFile info for {audio_file}:")
                print(f"  Size: {file_info['file_size_mb']:.2f} MB")
                print(f"  Format: {file_info['file_extension']}")
                print(f"  Supported: {file_info['is_supported_format']}")
                print(f"  Est. processing time: {file_info['estimated_processing_time']:.1f}s")
            except Exception as e:
                print(f"Error getting info for {audio_file}: {e}")


def tts_length_estimation_example():
    """Example of TTS length estimation."""
    print("\n=== TTS Length Estimation ===")
    
    tts = TextToSpeechDeepAI()
    
    texts = [
        "Short text.",
        "This is a medium length text that should take a bit longer to synthesize.",
        "This is a very long text that contains multiple sentences and should demonstrate the estimation capabilities of the text-to-speech system. It includes various words and punctuation to give a realistic estimate of synthesis time and cost."
    ]
    
    for i, text in enumerate(texts, 1):
        estimate = tts.get_text_length_estimate(text)
        print(f"\nText {i}:")
        print(f"  Words: {estimate['word_count']}")
        print(f"  Characters: {estimate['character_count']}")
        print(f"  Est. duration: {estimate['estimated_duration_seconds']:.1f}s")
        print(f"  Within limits: {estimate['is_within_limits']}")


def main():
    """Run all speech examples."""
    print("LangChain DeepAI - Speech Capabilities Examples")
    print("=" * 50)
    
    try:
        text_to_speech_example()
        different_voices_example()
        batch_tts_example()
        speech_to_text_example()
        batch_stt_example()
        audio_file_info_example()
        tts_length_estimation_example()
        
        print("\n" + "=" * 50)
        print("All speech examples completed!")
        print("Check the generated audio files in the current directory.")
        
    except Exception as e:
        print(f"Error running examples: {e}")
        print("Make sure you have set your DEEPAI_API_KEY environment variable.")


if __name__ == "__main__":
    main()
