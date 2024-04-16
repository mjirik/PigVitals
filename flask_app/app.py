from flask import Flask, render_template, request, redirect, url_for
import requests
from pymongo import MongoClient
import os

app = Flask(__name__)
client = MongoClient("mongodb://mongodb:27017/")
db = client.video_results

@app.route('/')
def index():
    videos = os.listdir('/usr/src/app/videos')
    return render_template('index.html', videos=videos)

@app.route('/process_video/<video_name>')
def process_video(video_name):
    video_processor_url = 'http://video_processor:8080/process'
    response = requests.post(video_processor_url, json={"path": f"/usr/src/app/videos/{video_name}"})
    if response.status_code == 200:
        data = response.json()
        return redirect(url_for('show_results', video_name=video_name, video_length=data['video_length'], number_of_frames=data['number_of_frames'], width=data['width'], height=data['height'], fps=data['fps']))
    else:
        data = response.json()
        error = data["error"]
        return error, 500

@app.route('/show_results')
def show_results():
    video_name = request.args.get('video_name')
    video_length = request.args.get('video_length')
    number_of_frames = request.args.get('number_of_frames')
    width = request.args.get('width')
    height = request.args.get('height')
    fps = request.args.get('fps')
    return render_template('results.html', video_name=video_name, video_length=video_length, number_of_frames=number_of_frames, width=width, height=height, fps=fps)

@app.route('/save_results', methods=['POST'])
def save_results():
    video_name = request.form['video_name']
    video_length = request.form['video_length']
    number_of_frames = request.form['number_of_frames']
    width = request.form['width']
    height = request.form['height']
    fps = request.form['fps']
    result = db.results.insert_one({
        "video_name": video_name,
        "video_length": video_length,
        "number_of_frames": number_of_frames,
        "width": width,
        "height": height,
        "fps": fps
    })
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
