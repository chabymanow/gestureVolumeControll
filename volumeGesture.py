from cv2 import FILLED
import mediapipe as mp
import cv2
import numpy as np
from mediapipe.framework.formats import landmark_pb2
import pywin32_system32
import math
import linearwinvolume

mp_drawing = mp.solutions.drawing_utils
mp_hands = mp.solutions.hands

video = cv2.VideoCapture(0)

# Setup the device on the first run
# It is needs to be done 
# linearwinvolume.setup()

with mp_hands.Hands(min_detection_confidence = 0.8, min_tracking_confidence = 0.5) as hands:
    while video.isOpened():
        _,frame = video.read()
        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image = cv2.flip(image, 1)

        image_width = 640
        image_height = 480
        results = hands.process(image)
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

        # Draw the finger landmarks and joints
        # if results.multi_hand_landmarks:
        #     for num, hand in enumerate(results.multi_hand_landmarks):
        #         mp_drawing.draw_landmarks(image, hand, mp_hands.HAND_CONNECTIONS,
        #             mp_drawing.DrawingSpec(color = (250, 44, 250), thickness = 2, circle_radius = 2))

        # If there is any hand ini the picture, check the landmarks        
        if results.multi_hand_landmarks != None:
            for handLandmarks in results.multi_hand_landmarks:
                for points in mp_hands.HandLandmark:
                    # Normalize the 3D coordinates to 2D
                    normalizedHandmark = handLandmarks.landmark[points]
                    pixelCoordinatesLandmark = mp_drawing._normalized_to_pixel_coordinates(normalizedHandmark.x, normalizedHandmark.y, image_width, image_height)
                    
                    points = str(points)
                    # Check the tip of thumb and store the actual coordinates
                    if points == 'HandLandmark.THUMB_TIP':
                        targetPoint_x = pixelCoordinatesLandmark[0]
                        targetPoint_y = pixelCoordinatesLandmark[1]

                    # Check the tip of index finger and store the actual coordinates
                    if points == 'HandLandmark.INDEX_FINGER_TIP':
                        try:       
                            # Draw circles on the tips and draw line between the two tips 
                            cv2.circle(image, (pixelCoordinatesLandmark[0], pixelCoordinatesLandmark[1]), 8, (0,255,0), 3)
                            cv2.circle(image, (targetPoint_x, targetPoint_y), 8, (0,255,0), 3)
                            cv2.line(image, (pixelCoordinatesLandmark[0], pixelCoordinatesLandmark[1]), (targetPoint_x, targetPoint_y), (0,255,0), 2)
                            indexfingertip_x = pixelCoordinatesLandmark[0]
                            indexfingertip_y = pixelCoordinatesLandmark[1]

                            # Calculate the distant between the two tips
                            dist = math.sqrt((targetPoint_x - indexfingertip_x)**2 + (targetPoint_y - indexfingertip_y)**2)
                            
                            # Convert the list to the other list to use it
                            size = np.interp(dist,[20, 210], [280, 80])
                            volume = np.interp(dist,[20, 210], [0, 100])
                            currVol = linearwinvolume.get_volume()

                            # Set the volume according the lenght of the line
                            linearwinvolume.set_volume(int(volume))

                            # Write out some informations and a volume bar, just for visualize the current settings
                            cv2.putText(image, f'Volume: {int(volume)}', (20, 40), cv2.FONT_HERSHEY_COMPLEX, .8, (255, 0, 0), 1)
                            cv2.putText(image, f'Current Volume: {int(currVol)}', (20, 70), cv2.FONT_HERSHEY_COMPLEX, .8, (255, 0, 0), 1)
                            cv2.rectangle(image, (50, 80), (80, 280), (255,0,0), 3)
                            cv2.rectangle(image, (80, 280), (50, int(size)), (255,255,0), FILLED)
                        except:
                            pass
    
        # Put out the window
        cv2.imshow('game', image)

        # Check the key press and quit if the 'q' key was pressed
        if cv2.waitKey(10) & 0xFF == ord('q'):
            break

# Delete the video and destroy the window. Quit from the application
video.release()
cv2.destroyAllWindows()