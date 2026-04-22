# Guardian-VLM: Automated Forensic Analysis & AI Dispatch System

##  Overview
Guardian-VLM is a next-generation public safety pipeline that bridges the gap between passive CCTV surveillance and active emergency response. The system autonomously processes video feeds using Vision-Language Models (VLMs) to detect critical incidents (e.g., assaults, accidents, weapons). 

Upon detecting a severe threat, it generates a structured forensic report and immediately triggers an AI-driven, two-way conversational voice agent. The system dynamically routes the call to the **nearest appropriate responder (e.g., a hospital for accidents, a police station for assaults)**, briefs them on the situation, and allows them to ask questions back to the AI in real-time.

##  Key Features
* **Automated Visual Forensics:** Utilizes Google Gemini 2.5 Flash to process video files and extract highly detailed, "Sherlock Holmes" style situational narratives, participant counts, and hazard assessments.
* **Context-Aware Dynamic Routing:** Automatically evaluates both the severity and the *type* of incident. Based on the event (e.g., violent assault vs. vehicle collision), it routes the emergency call to the nearest relevant facility (police station or hospital).
* **Two-Way Conversational Dispatch:** Integrates with the Bolna API to initiate outbound phone calls. The AI acts as a live dispatcher, explaining the scene to human responders and actively answering their follow-up questions.
* **Low-Latency Voice Switchboard:** Features a FastAPI WebSocket server utilizing Groq (Llama 3.3) for lightning-fast tactical reasoning and Sarvam AI (Bulbul V3) for localized Indian-English Text-to-Speech (TTS), enabling live Twilio media stream interactions.
* **Automated Documentation:** Generates and archives formal `.txt` incident reports for official police/security records.

##  System Architecture

1. **The Watcher (`main.py` & `video_handler.py`):** Scans directories for new video files and securely uploads them to the Gemini File API.
2. **The Brain (`llm_reasoning.py`):** Gemini 2.5 Flash analyzes the video and returns a strictly formatted JSON object (`IncidentReport`) detailing the event timeline, spatial layout, crowd dynamics, and incident type.
3. **The Dispatcher (`dispatcher.py`):** If the reasoning engine flags a critical event, it determines the nearest appropriate contact based on camera location and incident type. A payload is sent to Bolna AI to call that specific responder.
4. **The Switchboard (`server.py`):** A standalone FastAPI application that maintains a two-way WebSocket connection. Responders can speak directly to the AI to ask about the scene; the system processes the audio via Groq LLM and replies instantly using Sarvam AI synthetic voice.

##  Technology Stack
* **Language:** Python 3.10+
* **Vision-Language Model:** Google Gemini 2.5 Flash
* **Fast-Inference LLM:** Groq (Llama-3.3-70b-versatile)
* **Text-to-Speech:** Sarvam AI (Bulbul:v3)
* **Voice Agent Orchestration:** Bolna API
* **Web Framework:** FastAPI & Uvicorn

