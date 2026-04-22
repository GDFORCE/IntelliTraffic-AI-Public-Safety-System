import os
import json
from google import genai
import video_handler
import llm_reasoning
import dispatcher 

# Initialize the client
client = genai.Client(api_key="")

# ==========================================
# 🎥 THE MOCK CAMERA REGISTRY
# ==========================================
CAMERA_DATABASE = {
    "Fighting003_x264A.mp4": {
        "camera_id": "CAM-SUBWAY-04",
        "location": "Subway Platform 4, Times Square Station",
        "coords": (40.7580, -73.9855) 
    },
    "CarCrash_Test.mp4": { 
        "camera_id": "CAM-HWY-108",
        "location": "North Junction Highway, Exit 12",
        "coords": (40.7829, -73.9654) 
    }
}

def get_camera_metadata(filename):
    return CAMERA_DATABASE.get(filename, {
        "camera_id": "UNIT-UNKNOWN",
        "location": "Mobile Responder Unit",
        "coords": (40.7128, -74.0060) 
    })

def process_folder(folder_path):
    print(f"Scanning folder: {folder_path}")
    
    valid_extensions = (".mp4", ".avi", ".mov", ".mkv")
    video_files = [f for f in os.listdir(folder_path) if f.lower().endswith(valid_extensions)]
    
    if not video_files:
        print("No video files found.")
        return

    print(f"Found {len(video_files)} videos. Starting Guardian-VLM...\n")
    
    for video_file in video_files:
        full_path = os.path.join(folder_path, video_file)
        camera_info = get_camera_metadata(video_file)
        
        print(f"=== Now Processing: {video_file} (Location: {camera_info['location']}) ===")
        
        try:
            # 1. Prepare Video
            active_video = video_handler.upload_and_prepare_video(client, full_path)
            
            # 2. Get the Forensic Data (Expects the new JSON with visual_context)
            report_data = llm_reasoning.generate_forensic_report(client, active_video)
            
            # 3. Print the OFFICIAL REPORT for the Dashboard
            print("\n" + "="*50)
            print("OFFICER DASHBOARD: OFFICIAL INCIDENT REPORT")
            print("="*50)
            print(f"Camera ID: {camera_info['camera_id']}")
            print(f"Location:  {camera_info['location']}")
            print(f"Severity:  {report_data.get('severity', 'UNKNOWN')}")
            print("-" * 50)
            print(report_data.get("official_report", "No narrative available."))
            print("="*50 + "\n")
            
            # 4. SAVE the formal report to a .txt file
            base_name = os.path.splitext(video_file)[0]
            report_path = os.path.join(folder_path, f"{base_name}_Report.txt")
            
            with open(report_path, "w", encoding="utf-8") as file:
                file.write("GUARDIAN-VLM AUTOMATED FORENSIC REPORT\n")
                file.write(f"Location: {camera_info['location']} | ID: {camera_info['camera_id']}\n")
                file.write("="*40 + "\n\n")
                file.write(report_data.get("official_report", ""))
                
            print(f"📄 Official Report saved to: {base_name}_Report.txt")
            
            # 5. SMART DISPATCH (Trigger Voice AI Riley)
            # Use severity and weapons detection for the trigger
            if report_data.get("severity") in ["High", "Critical"] or report_data.get("has_weapons"):
                print(f"🚨 SYSTEM TRIGGER: EMERGENCY ALERT INITIATED! 🚨")
                
                # We pass the WHOLE report_data dictionary so dispatcher.py 
                # can send the 'visual_context' to Riley.
                dispatcher.route_emergency(report_data, camera_info)
            else:
                print(f"✅ SYSTEM TRIGGER: Scene stable. No immediate dispatch required.\n")
            
        except Exception as e:
            print(f"❌ Error processing {video_file}: {e}")

if __name__ == "__main__":
    # Ensure this path matches your local folder
    folder_path = r"D:\SDP\VLM" 
    process_folder(folder_path)
