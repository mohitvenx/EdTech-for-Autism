from PyQt5.QtCore import QUrl, Qt
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWidgets import QApplication
import os
import subprocess
import csv
import matplotlib
matplotlib.use('Agg')
import cv2
import matplotlib.pyplot as plt
import time
from flask import Flask, render_template, Response, redirect, request
from camera import VideoCamera
from gaze_tracking import GazeTracking
gaze = GazeTracking()


app = Flask(__name__)

CSV_FILE = 'user.csv'

def authenticate(username, password):
    with open(CSV_FILE, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if row['username'] == username and row['password'] == password:
                return True
    return False


le_pupil=[]
ri_pupil=[]

def generate_frames():
    webcam = cv2.VideoCapture(0)
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

@app.route('/')
def login():
    return render_template('start.html')

@app.route('/sign')
def sign():
    return render_template('index.html')

# Define the routes for each game
@app.route('/home')
def home():
    return render_template('home.html')

# This route will handle the login form submission
@app.route('/submit_login', methods=['POST'])
def submit_login():
    # Get the username and password from the form
    username = request.form['username']
    password = request.form['password']
    error = None
    print(password)
    if authenticate(username, password):
        return redirect('/home')
    else:
        error = 'Invalid username or password'
        return render_template('index-login.html', error=error)

@app.route('/sign_up', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
    
        with open(CSV_FILE, 'a', newline='') as csvfile:
            fieldnames = ['username','password']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            writer.writerow({'username': name,'password': password})

        return redirect('/sign')

@app.route('/index_gt')
def index_gt():
    time.sleep(3)
    return render_template('index_gt.html')

@app.route('/video_gaze')
def video_gaze():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/plot')
def plot():
    # Return left and right pupil coordinates
    le_x, le_y = zip(*le_pupil)
    ri_x, ri_y = zip(*ri_pupil)
    plot=['le_x', 'le_y','ri_x', 'ri_y']
    rows = [ [le_x],
         [le_y],
         [ri_x],
         [ri_y]]
    with open('GF5', 'w') as f:
     
    # using csv.writer method from CSV package
        write = csv.writer(f)
     
        write.writerow(plot)
        write.writerows(rows)
    plt.plot(le_x, le_y, 'bo', ri_x, ri_y, 'ro')
    plt.savefig('static/plot.png')
    plt.close()
    return render_template('plot_gt.html')
  
@app.route('/emotion')
def emotion():
    return render_template('index_em.html')

def gen(camera):
    while True:
        frame = camera.get_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(gen(VideoCamera()),mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/pygame', methods = ['POST', 'GET'])
def pygame():
    return render_template('memorygame.html')

@app.route('/pyqt5')
def pyqt5():
    launch_pyqt5()
    return render_template('home.html')

def launch_pyqt5():
    try:
        subprocess.Popen(['python', 'D:/Autism/word-search/source1.py'])
        return render_template('home.html', message='PyQt5 file launched successfully!')
    except Exception as e:
        return render_template('home.html', message='Error launching PyQt5 file: {}'.format(e))


@app.route('/balloon_pop_math')
def balloon_pop_math():
    return render_template('balloon_pop_math.html')

@app.route('/simonsays')
def simonsays():
    return render_template('index_simon_says.html')

@app.route('/launch_pyqt5', methods=['POST'])
def launch_pyqt5_button():
    launch_pyqt5()
    return render_template('pyqt5.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)