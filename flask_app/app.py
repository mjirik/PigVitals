from flask import Flask, render_template, request, redirect, url_for, send_from_directory, jsonify, current_app, send_file, abort
from pymongo import MongoClient
import requests
import os
import re

app = Flask(__name__)

# Setup MongoDB client
client = MongoClient("mongodb://mongodb:27017/")
db = client.video_db  # Adjust database name as needed
processed_videos = db.processed_videos

@app.route('/')
def index():
    videos = os.listdir('videos')
    processed_videos = os.listdir('static/processed')
    return render_template('index.html', videos=videos, processed_videos=processed_videos)


@app.route('/process_video/<video_name>')
def process_video_page(video_name):
    video_path = os.path.join('videos', video_name)
    response = requests.post('http://video_processor:8080/process', json={"path": video_path})
    if response.status_code == 200:
        json_data = response.json()
        processed_videos.insert_one(json_data)
        return redirect(url_for('show_processed_video', video_name=video_name))
    else:
        return jsonify({"error": "Processing failed"}), 500

@app.route('/show_processed_video/<video_name>')
def show_processed_video(video_name):
    video_data = db.processed_videos.find_one({"processed_path": {"$regex": f".*{video_name}$"}})
    if not video_data:
        return "Video not found", 404
    return render_template('show_processed_video.html', video_data=video_data, video_filename=video_name)


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
