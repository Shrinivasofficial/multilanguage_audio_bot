import speech_recognition as sr
import sounddevice as sd
import numpy as np
from langdetect import detect
from googletrans import Translator
from gtts import gTTS
import playsound
import os
import google.generativeai as genai

# Set up your API key
genai.configure(api_key='AIzaSyBouvRSS9IeVAXrbtYJy69slHADhax3-VA')

# Set up the model
model = genai.GenerativeModel('gemini-free')


def recognize_speech():
    recognizer = sr.Recognizer()
    duration = 5  # Record for 5 seconds
    sample_rate = 16000  # Standard sample rate

    print("Listening...")
    # Record audio with sounddevice
    recording = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1, dtype='int16')
    sd.wait()

    # Convert the NumPy array to bytes for AudioData
    audio_data = np.squeeze(recording)  # Remove the extra dimension
    audio_bytes = audio_data.tobytes()  # Convert to bytes

    # Convert the bytes to AudioData format expected by speech_recognition
    audio_data = sr.AudioData(audio_bytes, sample_rate, 2)

    try:
        text = recognizer.recognize_google(audio_data)
        print(f"You said: {text}")
        return text
    except sr.UnknownValueError:
        print("Sorry, I couldn't understand that. Please try again.")
        return None
    except sr.RequestError as e:
        print(f"Could not request results from Google Speech Recognition service; {e}")
        return None


def detect_language(text):
    try:
        return detect(text)
    except:
        print("Could not detect language. Defaulting to English.")
        return 'en'


def translate_text(text, source_language, target_language):
    translator = Translator()
    try:
        translation = translator.translate(text, src=source_language, dest=target_language)
        return translation.text
    except Exception as e:
        print(f"Translation error: {e}")
        return text  # Return original text if translation fails


def get_gemini_response(prompt, language):
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"Error getting response from Gemini: {e}")
        return "I'm sorry, I couldn't generate a response at the moment."


def text_to_speech(text, language):
    try:
        tts = gTTS(text=text, lang=language)
        tts.save("response.mp3")
        playsound.playsound("response.mp3")
        os.remove("response.mp3")
    except Exception as e:
        print(f"Text-to-speech error: {e}")
        print("Here's the text response:", text)


def main():
    print("Multilingual Gemini Speech Assistant")
    print("Speak in English, Hindi, or Tamil. Say 'exit' to quit.")

    while True:
        user_input = recognize_speech()
        if user_input:
            if user_input.lower() == 'exit':
                print("Exiting the program. Goodbye!")
                break

            language = detect_language(user_input)

            # Translate user input to English for Gemini if not already in English
            if language != 'en':
                english_input = translate_text(user_input, language, 'en')
            else:
                english_input = user_input

            # Get response from Gemini
            gemini_prompt = f"Please provide a concise response to the following question or statement: {english_input}"
            english_response = get_gemini_response(gemini_prompt, 'en')

            # Translate Gemini's response back to the original language if needed
            if language != 'en':
                response = translate_text(english_response, 'en', language)
            else:
                response = english_response

            print(f"Responding in {language}: {response}")

