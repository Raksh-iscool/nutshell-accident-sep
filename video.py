import threading
import pandas as pd
import numpy as np
import streamlit as st
import joblib
#from IPython import get_ipython
from PIL import Image
import cv2
import os
from ultralytics import YOLO
import tempfile
import image_to_text


r = 0


def display_tracker_options():
    display_tracker = st.radio("Display Tracker", ('Yes', 'No'))
    is_display_tracker = True if display_tracker == 'Yes' else False
    if is_display_tracker:
        tracker_type = st.radio("Tracker", ("bytetrack.yaml", "botsort.yaml"))
        return is_display_tracker, tracker_type
    return is_display_tracker, None

def _display_detected_frames(conf, model, st_frame, image, is_display_tracking=None, tracker=None):
    global de
    global r
    # Resize the image to a standard size
    image = cv2.resize(image, (720, int(720*(9/16))))

    # Display object tracking, if specified
    if is_display_tracking:
        res = model.track(image, conf=conf, persist=True,tracker=tracker)
    else:
        # Predict the objects in the image using the YOLOv8 model
        res = model.predict(image, conf=conf)

    r = r + len(res[0])
    # # Plot the detected objects on the video frame
    res_plotted = res[0].plot()
    
    st_frame.image(res_plotted,
                   caption='Detected Video',
                   channels="BGR",
                   use_column_width=True
                   )  
    #cv2.imwrite('accident_frame.jpg', image)
    if (res[0].boxes.is_track): 
        if de==0:
            cv2.imwrite('accident_frame.jpg', image)
            st.subheader(":red[Accident Detected]")
            t = threading.Thread(target=image_to_text.generate_and_send_report, args=('accident_frame.jpg', ['a.thirumurugan1211@gmail.com']))
            t.start()
            de = 1

    
    
    

def play_stored_video(video, conf, model):
    """
    Plays a stored video file. Tracks and detects objects in real-time using the YOLOv8 object detection model.

    Parameters:
        conf: Confidence of YOLOv8 model.
        model: An instance of the `YOLOv8` class containing the YOLOv8 model.

    Returns:
        None

    Raises:
        None
    """


    is_display_tracker, tracker = display_tracker_options()

    with open(video, 'rb') as video_file:
        video_bytes = video_file.read()
    if video_bytes:
        st.video(video_bytes)
    
    print(video)
    try:
        vid_cap = cv2.VideoCapture(str(video))
        print(vid_cap)
        st_frame = st.empty()
        while (vid_cap.isOpened()):
            success, image = vid_cap.read()
            if success:
                _display_detected_frames(conf,
                                            model,
                                            st_frame,
                                            image,
                                            is_display_tracker,
                                            tracker
                                            )
            else:
                vid_cap.release()
                break
    except Exception as e:
        st.sidebar.error("Error loading video: " + str(e))
        
            
def main():
    global de
    de = 0
    st.sidebar.title("Accident Detection (Upload Video to Detect the Accident)")
    source_vid = st.sidebar.file_uploader("Upload video here",type="mp4")
    if source_vid:
        #print(source_vid.name)
        with open(("files\{source_vid.name}"),"wb") as f:
            f.write(source_vid.getbuffer())

        path = f"{source_vid.name}"

        tfile = tempfile.NamedTemporaryFile(delete=False)
        tfile.write(source_vid.read())

        detect = st.sidebar.button("Submit")
        #is_display_tracker, tracker = display_tracker_options()
        #print(path)
        model = YOLO("best.pt")
        if detect:        
            play_stored_video(tfile.name,0.5,model)

        # if r > 0:
        #     st.subheader(":red[Accident Detected]")

if __name__=="__main__":
    main()
