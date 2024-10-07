import streamlit as st
import sounddevice as sd
import wave
import os
import google.generativeai as genai
from gtts import gTTS
import playsound
from langdetect import detect, DetectorFactory
import speech_recognition as sr

# Fix random seed for consistent results
DetectorFactory.seed = 0

# Configure your Gemini API key
genai.configure(api_key='AIzaSyDjTDOnn5cW93l0VH3AaAz5sXXXXXX')  # Update with your actual API key


# Function to record audio and save it as a WAV file
def record_audio(filename, duration=5, sample_rate=16000):
    st.write("Listening...")
    recording = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1, dtype='int16')
    sd.wait()  # Wait for the recording to complete

    # Save the recording as a WAV file
    with wave.open(filename, 'wb') as wf:
        wf.setnchannels(1)  # Mono
        wf.setsampwidth(2)  # 16-bit samples
        wf.setframerate(sample_rate)  # 16000 Hz sample rate
        wf.writeframes(recording.tobytes())

    st.success(f"Audio recorded and saved to {filename}")


# Function to recognize speech from a WAV file
def recognize_speech_from_file(filename, language='en-US'):
    recognizer = sr.Recognizer()

    try:
        with sr.AudioFile(filename) as source:
            audio = recognizer.record(source)  # Load audio from file
            st.write("Recognizing speech...")
            text = recognizer.recognize_google(audio, language=language)
            st.success(f"You said: {text}")
            return text
    except sr.UnknownValueError:
        st.error("Sorry, I couldn't understand that. Please try again.")
        return None
    except sr.RequestError as e:
        st.error(f"Could not request results from Google Speech Recognition service; {e}")
        return None


# Function to send prompt to Gemini and get the response
def get_gemini_response(prompt):
    try:
        model = genai.GenerativeModel('gemini-1.5-flash-latest')  # Use the free tier of the Gemini model
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        st.error(f"Error getting response from Gemini: {e}")
        return "I'm sorry, I couldn't generate a response at the moment."


# Function to convert text to speech
def text_to_speech(text, language='en'):
    try:
        tts = gTTS(text=text, lang=language)
        tts.save("response.mp3")
        playsound.playsound("response.mp3")
        os.remove("response.mp3")
    except Exception as e:
        st.error(f"Text-to-speech error: {e}")
        st.write("Here's the text response:", text)


# Streamlit application
def main():
    st.title("Voice Recognition and Response Application")
    st.write("Record your voice, and I'll respond!")

    # Define the file path for saving the audio
    audio_file = "recorded_audio.wav"

    # Record audio button
    if st.button("Record Audio"):
        record_audio(audio_file)

        # Recognize speech from the recorded file
        user_input = recognize_speech_from_file(audio_file)

        # Process the input if it's recognized
        if user_input:
            user_input = user_input.replace('*', '').strip()  # Clean input

            if not user_input:
                st.error("Empty input after cleaning. Please try again.")
            else:
                lang = detect(user_input)  # Detect language
                st.success(f"Detected language: {lang}")

                # Determine the response language
                if lang == 'ta':  # Tamil detected
                    speech_lang = 'ta-IN'
                elif lang in ['en', 'es', 'fr', 'de', 'it']:
                    speech_lang = lang
                else:
                    st.warning(f"Language '{lang}' is not supported for TTS. Defaulting to English.")
                    speech_lang = 'en'  # Default to English for unsupported languages

                gemini_prompt = f"Please provide a concise response to the following question or statement: {user_input}"
                gemini_response = get_gemini_response(gemini_prompt)

                # Display the response
                st.write(f"**Gemini Response:** {gemini_response}")

                # Convert response to speech
                text_to_speech(gemini_response, speech_lang)

        # Clean up by removing the audio file
        if os.path.exists(audio_file):
            os.remove(audio_file)


if __name__ == "__main__":
    main()
