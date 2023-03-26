import cv2
from flask import Flask, render_template, Response
from gaze_tracking import GazeTracking
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import time
app = Flask(__name__)
gaze = GazeTracking()
webcam = cv2.VideoCapture(0)

le_pupil=[]
ri_pupil=[]

def generate_frames():
    while True:
        # We get a new frame from the webcam
        _, frame = webcam.read()

        # We send this frame to GazeTracking to analyze it
        gaze.refresh(frame)

        frame = gaze.annotated_frame()
        text = ""

        if gaze.is_blinking():
            text = "Blinking"
        elif gaze.is_right():
            text = "Looking right"
        elif gaze.is_left():
            text = "Looking left"
        elif gaze.is_center():
            text = "Looking center"

        cv2.putText(frame, text, (90, 60), cv2.FONT_HERSHEY_DUPLEX, 1.6, (147, 58, 31), 2)

        left_pupil = gaze.pupil_left_coords()
        right_pupil = gaze.pupil_right_coords()

        if left_pupil is not None:
            le_pupil.append(left_pupil)
        if right_pupil is not None:
            ri_pupil.append(right_pupil)

        cv2.putText(frame, "Left pupil:  " + str(left_pupil), (90, 130), cv2.FONT_HERSHEY_DUPLEX, 0.9, (147, 58, 31), 1)
        cv2.putText(frame, "Right pupil: " + str(right_pupil), (90, 165), cv2.FONT_HERSHEY_DUPLEX, 0.9, (147, 58, 31), 1)

        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()

        yield (b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/gazetrack')
def index():
    time.sleep(3)
    return render_template('index_gt.html')

@app.route('/video_gaze')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/plot')
def plot():
    # Return left and right pupil coordinates
    le_x, le_y = zip(*le_pupil)
    ri_x, ri_y = zip(*ri_pupil)
    plt.plot(le_x, le_y, 'bo', ri_x, ri_y, 'ro')
    plt.savefig('static/plot.png')
    plt.close()
    return render_template('plot_gt.html')

if __name__ == '__main__':
    app.run(debug=True)