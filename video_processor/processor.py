from flask import Flask, request, jsonify
import cv2
import os
from pymongo import MongoClient

app = Flask(__name__)

# Establish a connection to the MongoDB server
client = MongoClient("mongodb://mongodb:27017/")
db = client.video_processsing_db  # Assuming 'video_db' is the database name
processed_videos = db.processed_videos  # Assuming 'processed_videos' is the collection name

@app.route('/process', methods=['POST'])
def process_video():
    video_path = request.json['path']
    output_directory = '/usr/src/app/static/processed'  # Path where videos are saved
    output_path = os.path.join(output_directory, os.path.basename(video_path))

    # Ensure video can be opened
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        return jsonify({"error": "Could not open video"}), 500

    # Set up parameters for saving the processed video
    fourcc = cv2.VideoWriter_fourcc(*'avc1')
    fps = cap.get(cv2.CAP_PROP_FPS)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

    frame_count = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        # Example processing: Add text overlay
        cv2.putText(frame, 'Processed', (10, 50), cv2.FONT_HERSHEY_SIMPLEX,
                    1, (255, 255, 255), 2, cv2.LINE_AA)
        out.write(frame)
        frame_count += 1

    cap.release()
    out.release()

    # Document to store in MongoDB
    video_metadata = {
        "original_path": video_path,
        "processed_path": output_path,
        "width": width,
        "height": height,
        "fps": fps,
        "frame_count": frame_count
    }

    # Insert the metadata into MongoDB
    #processed_videos.insert_one(video_metadata)

    return jsonify(video_metadata)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
