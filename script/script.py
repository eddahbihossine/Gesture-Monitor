import cv2
import mediapipe as mp
import pyautogui
import time

# Initialize MediaPipe Hands, Face Mesh, and Drawing Utils
mp_hands = mp.solutions.hands
mp_face_mesh = mp.solutions.face_mesh
mp_drawing = mp.solutions.drawing_utils

# Capture video from webcam
cap = cv2.VideoCapture(0)

# Screen dimensions for scaling hand movements to screen size
screen_width, screen_height = pyautogui.size()

# Function to detect if a finger is raised
def is_finger_up(landmarks, finger_tip_id, finger_dip_id):
    return landmarks[finger_tip_id].y < landmarks[finger_dip_id].y

# Linear interpolation (LERP) function for smooth motion
def lerp(start, end, t):
    return start + (end - start) * t

# Function to detect blink by comparing eyelid distances
def is_blinking(landmarks):
    # Left eye landmarks (indexes for eye coordinates)
    left_eye_top = landmarks[159].y
    left_eye_bottom = landmarks[145].y
    
    # Right eye landmarks
    right_eye_top = landmarks[386].y
    right_eye_bottom = landmarks[374].y

    # Calculate the distance between the top and bottom eyelid
    left_eye_distance = abs(left_eye_top - left_eye_bottom)
    right_eye_distance = abs(right_eye_top - right_eye_bottom)

    # Threshold for detecting a blink (tune this value if needed)
    blink_threshold = 0.02

    # Return True if both eyes are blinking
    return left_eye_distance < blink_threshold and right_eye_distance < blink_threshold

# Initialize variables for mouse smoothing
mouse_x, mouse_y = pyautogui.position()
smooth_factor = 0.2  # Adjust for smoothness (lower = smoother, higher = faster movement)

# Initialize MediaPipe Hands and Face Mesh
with mp_hands.Hands(static_image_mode=False, max_num_hands=1, min_detection_confidence=0.7, min_tracking_confidence=0.5) as hands, \
     mp_face_mesh.FaceMesh(static_image_mode=False, max_num_faces=1, min_detection_confidence=0.7, min_tracking_confidence=0.5) as face_mesh:
    
    while cap.isOpened():
        success, image = cap.read()
        if not success:
            print("Ignoring empty frame.")
            continue

        # Flip the image horizontally for a selfie view
        image = cv2.flip(image, 1)

        # Convert the image color (OpenCV uses BGR, while MediaPipe uses RGB)
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        # Process the image to find hands
        hand_results = hands.process(image_rgb)

        # Process the image to find face mesh
        face_results = face_mesh.process(image_rgb)

        # Draw hand landmarks on the image if any hand is detected
        if hand_results.multi_hand_landmarks:
            for hand_landmarks in hand_results.multi_hand_landmarks:
                # Draw landmarks and connections between them
                mp_drawing.draw_landmarks(image, hand_landmarks, mp_hands.HAND_CONNECTIONS)

                # Get index finger tip coordinates for mouse control
                index_finger_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
                index_x = int(index_finger_tip.x * screen_width)
                index_y = int(index_finger_tip.y * screen_height)

                # Smoothly interpolate the mouse position
                mouse_x = lerp(mouse_x, index_x, smooth_factor)
                mouse_y = lerp(mouse_y, index_y, smooth_factor)
                pyautogui.moveTo(int(mouse_x), int(mouse_y))

                # Detect raised fingers
                index_finger_up = is_finger_up(hand_landmarks.landmark, mp_hands.HandLandmark.INDEX_FINGER_TIP, mp_hands.HandLandmark.INDEX_FINGER_DIP)
                middle_finger_up = is_finger_up(hand_landmarks.landmark, mp_hands.HandLandmark.MIDDLE_FINGER_TIP, mp_hands.HandLandmark.MIDDLE_FINGER_DIP)
                ring_finger_up = is_finger_up(hand_landmarks.landmark, mp_hands.HandLandmark.RING_FINGER_TIP, mp_hands.HandLandmark.RING_FINGER_DIP)

                # Count the number of fingers up
                fingers_up = [index_finger_up, middle_finger_up, ring_finger_up]
                num_fingers_up = sum(fingers_up)

                # Perform actions based on the number of fingers raised
                if num_fingers_up == 1:  # Click
                    print("1 finger up: Click")
                    pyautogui.click()
                if(num_fingers_up == 2):
                    print("2 fingers up: Scroll")
                    pyautogui.scroll(10)
                if(num_fingers_up == 3):
                    print("3 fingers up: Right click")
                    pyautogui.rightClick()
                

        # Draw face landmarks and check for blinking
        if face_results.multi_face_landmarks:
            for face_landmarks in face_results.multi_face_landmarks:
                # Draw face mesh landmarks on the image
                mp_drawing.draw_landmarks(image, face_landmarks, mp_face_mesh.FACEMESH_TESSELATION)

                # Check if the person is blinking
                if is_blinking(face_landmarks.landmark):
                    print("Blink detected: Click")
                    pyautogui.click()

        # Show the image with the drawn landmarks
        cv2.imshow('Hand & Face Gesture Control', image)

        # Press 'q' to exit
        if cv2.waitKey(5) & 0xFF == ord('q'):
            break

cap.release()
cv2.destroyAllWindows()
