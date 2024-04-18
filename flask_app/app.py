from flask import Flask, render_template, request, redirect, url_for, send_from_directory, jsonify, current_app, send_file, abort
from pymongo import MongoClient
import requests
import plotly.express as px
import pandas as pd
import os


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

@app.route('/get-plots')
def get_plots():
    # Data and plots definitions
    df1 = pd.DataFrame({
        'x': range(10),
        'y': [x**2 for x in range(10)]
    })
    fig1 = px.line(df1, x='x', y='y', title='Plot 1: y = x^2')

    df2 = pd.DataFrame({
        'x': range(10),
        'y': [x*2 for x in range(10)]
    })
    fig2 = px.line(df2, x='x', y='y', title='Plot 2: y = 2x')

    # Generating HTML for both plots
    plot1_html = fig1.to_html(full_html=False)
    plot2_html = fig2.to_html(full_html=False)

    return jsonify(plot1_html=plot1_html, plot2_html=plot2_html)

@app.route('/show_processed_video/<video_name>')
def show_processed_video(video_name):
    video_data = db.processed_videos.find_one({"processed_path": {"$regex": f".*{video_name}$"}})
    if not video_data:
        return "Video not found", 404
    return render_template('show_processed_video.html', video_data=video_data, video_filename=video_name)


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
