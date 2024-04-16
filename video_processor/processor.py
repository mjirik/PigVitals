from flask import Flask, request, jsonify
import cv2  # Import OpenCV
import os

app = Flask(__name__)

@app.route('/process', methods=['POST'])
def process_video():
    video_path = request.json['path']
    if not os.path.exists(video_path):
        return jsonify({"error": "File not found"}), 404

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        return jsonify({"error": "Could not open video"}), 500

    width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
    height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
    fps = cap.get(cv2.CAP_PROP_FPS)
    cap.release()

    return jsonify({"video_length": "Not computed", "number_of_frames": "Not computed", "width": int(width), "height": int(height), "fps": fps}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
