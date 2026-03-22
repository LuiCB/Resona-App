import os
import requests
import json
import time

import predict 


API_KEY = os.environ["EIGENAI_API_KEY"]
BOSON_AI_API_KEY = os.environ["BOSON_AI_API_KEY"]


def ars_audio(file_path: str) -> str:
    # read audio file, use the predict function in `predict.py` to get the transcription, and return the text
    print("Transcribing audio by Boson AI ARS ... ")
    transcript = predict.predict(audio_path=file_path,
                                user_text="Your task is to listen to audio input and output the exact spoken words as plain text in English.",
                                api_key=BOSON_AI_API_KEY)
    return transcript


def speech_behavioral_analysis(file_path: str) -> str:
    # read audio file, use the predict function in `predict.py` to get the behavioral analysis, and return the result as a dictionary
    print("Analyzing speech behavior by Boson AI Audio-understanding-v3.5 ... ")
    analysis = predict.predict(audio_path=file_path,
                               user_text=(
                                   "Analyze the speaker's vocal behavior and output EXACTLY this numbered format:\n"
                                   "1. Emotional Tone: <describe the speaker's emotional state and tone>\n"
                                   "2. Speaking Energy: <describe pace, volume, and energy level>\n"
                                   "3. Fluency Patterns: <describe hesitations, filler words, flow>\n"
                                   "4. Voice Quality: <describe pitch, warmth, resonance>\n"
                                   "5. Engagement Level: <describe how engaged or invested the speaker sounds>\n"
                                   "6. Notable Shifts: <describe any changes in tone, pace, or energy during the recording>\n"
                                   "Output in English."
                               ),
                               api_key=BOSON_AI_API_KEY)
    return analysis

def qwen_chat_completion(messages: list[dict], max_retries: int = 5) -> str:
    url = "https://api-web.eigenai.com/api/v1/chat/completions"
    headers = {
        "Authorization": API_KEY,
        "Content-Type": "application/json"
    }
    payload = {
        "model": "gpt-oss-120b",
        "messages": messages,
        "temperature": 0.7,
        "max_tokens": 10000,
        "stream": False
    }

    for attempt in range(max_retries):
        response = requests.post(url, headers=headers, json=payload)
        if response.status_code == 429:
            wait = 2 ** attempt  # 1s, 2s, 4s, 8s, 16s
            print(f"[gpt-oss] Rate limited (429). Retrying in {wait}s... (attempt {attempt + 1}/{max_retries})")
            time.sleep(wait)
            continue
        response.raise_for_status()
        return response.json()['choices'][0]['message']['content']

    # Final attempt after all retries
    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()
    return response.json()['choices'][0]['message']['content']


