import os
import json
import base64
import asyncio
import requests
import audioop
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from groq import Groq # <--- Switched to Groq
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

# Clients
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
SARVAM_API_KEY = os.getenv("SARVAM_API_KEY")

# --- 1. THE BRAIN (Groq LLM) ---
async def get_llm_response(transcript, report_text):
    """
    Uses Groq for ultra-low latency tactical reasoning.
    """
    system_prompt = f"""
    You are the Guardian-VLM Emergency Dispatcher. 
    LATEST FORENSIC REPORT: {report_text}
    
    INSTRUCTIONS: 
    - Answer using ONLY the report data.
    - Be brief (max 15 words). 
    - Use professional, calm Indian-English.
    - Provide specific tactical details from the report (e.g. 'one person on tracks').
    """
    
    # Using Llama 3.3 for lightning fast response
    chat_completion = groq_client.chat.completions.create(
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": transcript}
        ],
        model="llama-3.3-70b-versatile",
    )
    return chat_completion.choices[0].message.content

# --- 2. THE VOICE (Sarvam Bulbul V3) ---
def get_bulbul_v3_tts(text):
    url = "https://api.sarvam.ai/text-to-speech"
    headers = {"api-subscription-key": SARVAM_API_KEY}
    payload = {
        "inputs": [text],
        "target_language_code": "en-IN",
        "speaker": "meera", 
        "model": "bulbul:v3" # Upgraded to V3
    }

    response = requests.post(url, json=payload, headers=headers)
    if response.status_code == 200:
        # Convert to Mu-law for Twilio
        audio_content = response.content
        mulaw_audio = audioop.lin2ulaw(audio_content[44:], 2) 
        return base64.b64encode(mulaw_audio).decode('utf-8')
    return None

# --- 3. THE SWITCHBOARD ---
@app.websocket("/stream")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    print("📞 [Twilio] Conversational Stream Connected.")
    
    current_report = "Critical fight at Subway Platform 4. Subject pushed to tracks. Train arrived."
    audio_buffer = bytearray()
    stream_sid = None

    try:
        while True:
            message = await websocket.receive_text()
            data = json.loads(message)

            if data['event'] == "start":
                stream_sid = data['start']['streamSid']
                print(f"🚀 Stream {stream_sid} started.")

            elif data['event'] == "media":
                payload = data['media']['payload']
                audio_buffer.extend(base64.b64decode(payload))

                # Processing every 1 second of audio for better responsiveness
                if len(audio_buffer) > 8000: 
                    # 1. Mock/Real STT logic here 
                    transcript = "What is the status of the person on the tracks?" 
                    
                    print(f"👤 Officer: {transcript}")
                    
                    # 2. LLM via Groq (Super fast)
                    reply_text = await get_llm_response(transcript, current_report)
                    print(f"🤖 Dispatcher: {reply_text}")
                    
                    # 3. TTS via Bulbul V3
                    audio_payload = get_bulbul_v3_tts(reply_text)
                    
                    if audio_payload:
                        await websocket.send_json({
                            "event": "media",
                            "streamSid": stream_sid,
                            "media": {"payload": audio_payload}
                        })
                    audio_buffer.clear()

    except Exception as e:
        print(f"❌ WebSocket Error: {e}")
    finally:
        await websocket.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)