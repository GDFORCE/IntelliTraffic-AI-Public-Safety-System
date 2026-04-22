import json
from pydantic import BaseModel, Field
from google.genai import types

# ONLY changed the field names here to match your prompt and main.py
class IncidentReport(BaseModel):
    incident_detected: bool = Field(description="True if an accident, violence, or hazard is detected.")
    incident_type: str = Field(description="e.g., 'Assault', 'Vehicle Collision', 'Theft', 'Suspicious Activity','fighting'")
    severity: str = Field(description="Contextually assess as: 'Low', 'Medium', 'High', or 'Critical'.")
    has_weapons: bool = Field(description="True ONLY if an object is actively being used or brandished as a weapon.")
    official_report: str = Field(description="The complete, formal 6-section narrative incident report.")
    visual_context: str = Field(description="The Sherlock Holmes style narrative for the voice agent.")
    participants_count: int = Field(description="Precise number of individuals involved.")

def generate_forensic_report(client, video_file):
    print("Generating AI-Reasoned Incident Report...")
    
    prompt = """
You are the Guardian-VLM Forensic Analyst. Your mission is to provide a high-fidelity 
visual intelligence brief for a live emergency dispatcher.

### OUTPUT REQUIREMENT ###
Return a valid JSON object with the following keys:

1. "severity": (String) Choose from "Low", "Medium", "High", "Critical".
2. "official_report": (String) A formal, structured summary for police records including:
   - Incident Type
   - Timeline of events
   - Environmental Hazards
   - Final Outcome
3. "visual_context": (String) This is the "EYES" for our voice agent. Describe the scene 
   using the "Sherlock Holmes" method. Include:
   - SPATIAL LAYOUT: Where are people located relative to landmarks (e.g., "near the 
     yellow pillar," "at the edge of Platform 4").
   - DESCRIPTORS: Specific clothing colors and styles (e.g., "male in a neon green 
     jacket," "person with a black backpack").
   - ACTION SEQUENCE: Second-by-second breakdown of movements (e.g., "at 0:45, the 
     subject in the red hoodie lunges forward").
   - VULNERABILITIES: Specific risks (e.g., "The victim is stumbling and looks disoriented 
     near the track edge").
   - CROWD DYNAMICS: Are bystanders helping, fleeing, or recording?
4. "participants_count": (Integer) Precise number of individuals directly involved.
5. "has_weapons": (Boolean) True/False.

### TONE FOR VISUAL_CONTEXT ###
Write the 'visual_context' as if you are whispering into a radio to a partner. Use descriptive 
but punchy English. Avoid "The video shows..." and instead use "I can see..." or "Right now, 
the situation is...".
"""

    response = client.models.generate_content(
        model="gemini-2.5-flash", 
        contents=[prompt, video_file],
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=IncidentReport,
            temperature=0.2 
        )
    )
    
    return json.loads(response.text)