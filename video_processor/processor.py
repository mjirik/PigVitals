from flask import Flask, request, jsonify
import os  # For accessing file properties

app = Flask(__name__)

@app.route('/process', methods=['POST'])
def process_video():
    video_path = request.json['path']
    # Here you would add your real video processing logic
    video_length = 120  # Placeholder for video length in seconds
    number_of_frames = 3600  # Placeholder for number of frames
    return jsonify({"video_length": video_length, "number_of_frames": number_of_frames})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
