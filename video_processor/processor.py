from flask import Flask, request, jsonify
import cv2
import os
from pymongo import MongoClient
import json
from datetime import date
import numpy as np
import mmcv
from mmtrack.apis import inference_mot, init_model
from mmdet.apis import inference_detector, init_detector

app = Flask(__name__)

# Establish a connection to the MongoDB server
client = MongoClient("mongodb://mongodb:27017/")
db = client.video_processsing_db  # Assuming 'video_db' is the database name
processed_videos = db.processed_videos  # Assuming 'processed_videos' is the collection name

@app.route('/process', methods=['POST'])
def process_video():
    current_date = date.today()
    video_path = request.json['path']
    output_directory = '/usr/src/app/static/processed'  # Path where videos are saved
    output_path = os.path.join(output_directory, os.path.basename(video_path))
    mot_config = '/usr/src/app/mmtracking/configs/mot/deepsort/deepsort_faster-rcnn_fpn_4e_mot17-private-half.py'
    mot_model = init_model(mot_config, device='cuda:0')

    det_config = '/usr/src/app/mmdetection/configs/faster_rcnn/DP_faster_rcnn_r50_multiclass_detector.py'
    det_checkpoint = '/usr/src/app/mmdetection/checkpoints/epoch_10.pth'
    det_model = init_detector(det_config, det_checkpoint, device='cuda:0')

    input_video = video_path
    imgs = mmcv.VideoReader(input_video)
    prog_bar = mmcv.ProgressBar(len(imgs))

    trajectories = {}
    distances_walked = {}
    scale_factor = 0
    unique_pigs = set()

    outputs = {}
    fourcc = cv2.VideoWriter_fourcc(*'avc1')
    fps = imgs.fps
    width = imgs.width
    height = imgs.height
    frame_count = len(imgs)
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

    for i, img in enumerate(imgs):
        result = inference_mot(mot_model, img, frame_id=i)
        outputs[i] = result
        img_with_tracks = img.copy()  # Make a copy to draw on

        # Perform detection and calculate scale factor for the first frame
        if i == 0:
            result_det = inference_detector(det_model, img)
            scale_factor = calculate_scale_factor(result_det, det_model)

        light_status = is_daytime(img)
        if light_status:
            light_status_text = 'ON'
        else:
            light_status_text = 'OFF'

        if 'track_bboxes' in result and result['track_bboxes']:
            track_bboxes = result['track_bboxes'][0]  # Assuming there's only one array in 'track_bboxes'

            for track in track_bboxes:
                object_id = int(track[0])  # Object ID
                bbox = track[1:5]  # Bounding box coordinates

                center = (
                (bbox[0] + bbox[2]) / 2, (bbox[1] + bbox[3]) / 2)  # Calculate the centroid of the bounding box
                unique_pigs.add(object_id)

                if object_id not in trajectories:
                    trajectories[object_id] = [center]
                    distances_walked[object_id] = 0
                else:
                    distance = calculate_distance(center, trajectories[object_id][-1])
                    if distance > 1.5:
                        distances_walked[object_id] += distance * scale_factor / 100  # na metry
                    trajectories[object_id].append(center)
                cv2.rectangle(img_with_tracks, (int(bbox[0]), int(bbox[1])), (int(bbox[2]), int(bbox[3])), (255, 0, 0),
                              2)
                cv2.putText(img_with_tracks, f'PIG: {object_id}', (int(bbox[0]), int(bbox[1] - 10)),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 255, 255), 2)

        for object_id, points in trajectories.items():
            for j in range(1, len(points)):
                cv2.line(img_with_tracks, (int(points[j - 1][0]), int(points[j - 1][1])),
                         (int(points[j][0]), int(points[j][1])), (255, 0, 0), 2)  # Draw line
            text = f'Pig {object_id}: {distances_walked[object_id]:.2f} m'
            cv2.putText(img_with_tracks, text, (10, 30 + 30 * object_id), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 1,
                        cv2.LINE_AA)

        # Save the frame with drawn bounding boxes and trajectories
        cv2.putText(img_with_tracks, f'Lights status: {light_status_text}', (20, 630), cv2.FONT_HERSHEY_SIMPLEX, 1,
                    (0, 0, 0), 2)
        cv2.putText(img_with_tracks, f'Number of Pigs: {len(unique_pigs)}', (20, 600), cv2.FONT_HERSHEY_SIMPLEX, 1,
                    (0, 0, 0), 2)
        prog_bar.update()
        out.write(img_with_tracks)

    out.release()

    json_data = json.dumps(outputs, default=convert_ndarray_to_list)
    data = json.loads(json_data)

    video_metadata = {
        "original_path": video_path,
        "processed_path": output_path,
        "video_data": data,
        "width": width,
        "height": height,
        "fps": fps,
        "frame_count": frame_count,
        "camera": "zverinec01",
        "scale_factor": scale_factor,
        "date_processed": current_date
        }

    return jsonify(video_metadata)

# Function to calculate distance between two points
def calculate_distance(point1, point2):
    return np.sqrt((point2[0] - point1[0]) ** 2 + (point2[1] - point1[1]) ** 2)

def calculate_scale_factor(result_det, det_model):
    desired_classes = ['feeder_full', 'feeder_empty']
    class_ids = [det_model.CLASSES.index(cls) for cls in desired_classes if cls in det_model.CLASSES]

    filtered_result = []
    for i, bbox in enumerate(result_det):
        if i in class_ids:
            filtered_result.append(bbox)

    # Show the result using mmcv
    #if filtered_result:
    #    show_result_pyplot(model, img, filtered_result)

    corners = []

    for bboxes in filtered_result:
        if isinstance(bboxes, np.ndarray):
            for bbox in bboxes:
                if len(bbox) < 5:  # ensure bbox has at least 5 elements [x1, y1, x2, y2, score]
                    continue
                # Upper right corner (x2, y1)
                upper_right = (bbox[2], bbox[1])
                # Lower right corner (x2, y2)
                lower_right = (bbox[2], bbox[3])
                corners.append((upper_right, lower_right))
        elif isinstance(bboxes, list):  # In case the bboxes are stored as a list of tensors
            for bbox_tensor in bboxes:
                bbox = bbox_tensor.cpu().numpy()  # Convert tensor to numpy array if necessary
                # Upper right corner (x2, y1)
                upper_right = (bbox[2], bbox[1])
                # Lower right corner (x2, y2)
                lower_right = (bbox[2], bbox[3])
                corners.append((upper_right, lower_right))

    distances = []

    for upper_right, lower_right in corners:
        # Calculate the Euclidean distance between the upper right and lower right corners
        distance = np.sqrt((upper_right[0] - lower_right[0]) ** 2 + (upper_right[1] - lower_right[1]) ** 2)
        distances.append(distance)

    # Calculate the mean of the distances
    mean_distance = np.mean(distances)
    scale_factor = 77/mean_distance # koryto má 77cm

    return scale_factor

def is_daytime(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    mean_brightness = np.mean(gray)

    threshold = 100

    if mean_brightness > threshold:
        return True
    else:
        return False

def convert_ndarray_to_list(obj):
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, dict):
        return {k: convert_ndarray_to_list(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_ndarray_to_list(item) for item in obj]
    else:
        return obj

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
