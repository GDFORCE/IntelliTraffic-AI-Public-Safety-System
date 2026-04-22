import os
import requests
from dotenv import load_dotenv

load_dotenv()

# Bolna Credentials
BOLNA_API_KEY = os.getenv("BOLNA_API_KEY")
BOLNA_AGENT_ID = os.getenv("BOLNA_AGENT_ID")

def route_emergency(report_data, camera_info):
    """
    Triggers the Pro Conversational Agent on Bolna.
    Now accepts the full report_data dictionary to provide deep visual context.
    """
    print(f"🧠 [Bolna AI] Initiating Pro Conversational Dispatch...")

    # Bolna's outgoing call endpoint
    url = "https://api.bolna.ai/call" 
    
    headers = {
        "Authorization": f"Bearer {BOLNA_API_KEY}",
        "Content-Type": "application/json"
    }

    # 1. Extract the Visual Narrative for the Voice Agent
    # We prioritize 'visual_context' because it contains the descriptions 
    # of clothes, positions, and landmarks that make the agent sound natural.
    if isinstance(report_data, dict):
        incident_context = report_data.get("visual_context", "A high-priority incident is unfolding.")
        severity = report_data.get("severity", "Unknown")
    else:
        # Fallback if a simple string was passed
        incident_context = report_data
        severity = "High"

    # 2. Add metadata to the context so Riley knows WHERE he is looking
    location_string = f"LOCATION: {camera_info['location']} (Camera: {camera_info['camera_id']}). "
    full_context_for_bolna = location_string + incident_context

    payload = {
        "agent_id": BOLNA_AGENT_ID,
        "recipient_phone_number": os.getenv("MY_PERSONAL_NUMBER"),
        "from_phone_number": os.getenv("TWILIO_PHONE_NUMBER"),
        "user_data": {
            # This MUST match the {{incident_report}} variable in your Bolna LLM prompt
            "incident_report": full_context_for_bolna
        }
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
        
        if response.status_code in [200, 201]:
            print(f"✅ Pro Dispatcher Active! Calling {os.getenv('MY_PERSONAL_NUMBER')} now.")
        else:
            print(f"❌ Bolna Error: {response.status_code} - {response.text}")
            print(f"💡 Tip: Ensure your Agent ID {BOLNA_AGENT_ID} is active and published.")
            
    except Exception as e:
        print(f"❌ Failed to connect to Bolna: {e}")