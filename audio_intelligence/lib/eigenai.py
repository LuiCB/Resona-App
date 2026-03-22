import requests
import json
# import requests


api_key = "sk-c6f382c0_0f4aab2970f04cedb3f26961ff996116abf6f4f7bc90b7d2b19259b4bda3b883"

# url = "https://api-web.eigenai.com/api/v1/generate"
# headers = {"Authorization": api_key}

# with open("describe_place_completely_at_ease.wav", "rb") as audio:  # Replace with your local audio path
#     files = {"file": ("describe_place_completely_at_ease.wav", audio, "audio/wav")}
#     data = {
#         "model": "higgs_asr_3",
#         "language": "English"
#     }

#     response = requests.post(url, headers=headers, data=data, files=files)
#     response.raise_for_status()
#     print(response.json())

url = "https://api-web.eigenai.com/api/v1/chat/completions"
headers = {
    "Authorization": api_key,
    "Content-Type": "application/json"
}
payload = {
    "model": "qwen3-30b-fp8",
    "messages": [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": '''Summarize the following text: The speaker's emotional state appears calm, reflective, and at ease, conveying a sense of peace and acceptance. Their communication style is gentle, descriptive, and unhurried, with a focus on sensory details and a deliberate pacing that mirrors the tranquility they describe. The use of soft, flowing language—such as "gently," "pale and soft," "warm and golden," and "suspended stillness"—suggests a soothing and meditative tone. Notable vocal patterns include a rhythmic cadence, repetition of calming imagery, and a preference for understated, almost poetic phrasing that emphasizes presence over action. The speaker seems to value stillness, introspection, and the beauty of ordinary moments, creating a narrative that feels intimate and comforting.'''}
    ],
    "temperature": 0.7,
    "max_tokens": 2048,
    "stream": False
}

response = requests.post(url, headers=headers, json=payload)
response.raise_for_status()
print(json.dumps(response.json(), indent=2))

