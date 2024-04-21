from flask import Flask, render_template, request, redirect, url_for, send_from_directory, jsonify, current_app, send_file, abort
from pymongo import MongoClient
import requests
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import os
import numpy as np


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

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/process_video/<video_name>')
def process_video_page(video_name):
    # Directly return the loading page
    return render_template('processing.html', video_name=video_name)

@app.route('/start_processing/<video_name>', methods=['POST'])
def start_processing(video_name):
    video_path = os.path.join('videos', video_name)
    response = requests.post('http://video_processor:8080/process', json={"path": video_path})
    if response.status_code == 200:
        json_data = response.json()
        processed_videos.insert_one(json_data)
        return jsonify({'status': 'started'})
    else:
        return jsonify({'error': 'Failed to start processing'}), 500

@app.route('/get-plots/<video_name>')
def get_plots(video_name):
    data = db.processed_videos.find_one({"processed_path": {"$regex": f".*{video_name}$"}})
    video_outputs = data["video_data"]
    scale_factor = data["scale_factor"]
    frame_height = data["height"]  # This assumes frame height is stored in the data
    trajectories = {}

    # Iterate over frames
    for frame, values in video_outputs.items():
        # Access track_bboxes
        for bbox in values['track_bboxes']:
            # Extract object ID
            object_id = int(bbox[0][0])
            # Extract center coordinates, flipping the y-coordinate
            center_x = (bbox[0][1] + bbox[0][3]) / 2
            center_y = frame_height - (bbox[0][2] + bbox[0][4]) / 2  # Flip the y-coordinate
            # Add center coordinates to trajectory for object
            if object_id not in trajectories:
                trajectories[object_id] = {'x': [], 'y': []}
            trajectories[object_id]['x'].append(center_x)
            trajectories[object_id]['y'].append(center_y)

    # Convert trajectories into a DataFrame for plotting
    data = []
    for object_id, trajectory in trajectories.items():
        for x, y in zip(trajectory['x'], trajectory['y']):
            data.append({'object_id': object_id, 'X': x, 'Y': y})

    df = pd.DataFrame(data)
    # Create a scatter plot using Plotly
    fig1 = px.scatter(df, x='X', y='Y', color='object_id', labels={'object_id': 'Prase ID'},
                      title='Nachozená trajektorie')

    # Update plot layout
    fig1.update_layout(xaxis_title='X', yaxis_title='Y', showlegend=False)

    # Convert the plot to HTML for embedding
    plot1_html = fig1.to_html(full_html=False)

    distances = {}
    for object_id, trajectory in trajectories.items():
        x = trajectory['x']
        y = trajectory['y']
        total_distance = 0
        for i in range(len(x) - 1):
            dx = x[i + 1] - x[i]
            dy = y[i + 1] - y[i]
            distance = np.sqrt(dx ** 2 + dy ** 2)
            if distance > 1.5:
                total_distance += distance * scale_factor / 100
        distances[object_id] = total_distance

    # Create bar chart of distances
    fig2 = go.Figure(data=[go.Bar(x=list(distances.keys()), y=list(distances.values()))])

    # Update layout
    fig2.update_layout(
        title='Nachozená vzdálenost [m]',
        xaxis_title='Prase ID',
        yaxis_title='Vzádlenost',
        showlegend = False
    )
    # Generating HTML for both plots

    plot2_html = fig2.to_html(full_html=False)

    return jsonify(plot1_html=plot1_html, plot2_html=plot2_html)

@app.route('/show_processed_video/<video_name>')
def show_processed_video(video_name):
    video_data = db.processed_videos.find_one({"processed_path": {"$regex": f".*{video_name}$"}})
    if not video_data:
        return "Video not found", 404
    video_filename = os.path.basename(video_data['processed_path'])
    return render_template('show_processed_video.html', video_data=video_data, video_filename=video_filename)

@app.route('/check_video_exists/<video_name>')
def check_video_exists(video_name):
    processed_video_path = os.path.join('static/processed', video_name)
    exists = os.path.exists(processed_video_path)
    return jsonify({'exists': exists})

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
