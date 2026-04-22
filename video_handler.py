import time

def upload_and_prepare_video(client, video_path):
    print(f"Uploading video: {video_path}...")
    
    # Upload to Gemini File API
    video_file = client.files.upload(file=video_path)
    print("Video uploaded. Processing metadata...")

    # Poll for status
    while video_file.state.name == "PROCESSING":
        time.sleep(2)
        video_file = client.files.get(name=video_file.name)

    if video_file.state.name == "FAILED":
        raise ValueError(f"Video processing failed for {video_path}")

    print("Video is ACTIVE and ready for analysis.")
    return video_file