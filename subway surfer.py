import sys
import cv2
import mediapipe
import autopy
import time

cap = cv2.VideoCapture(0)

# Initializing mediapipe
initHand = mediapipe.solutions.hands
mainHand = initHand.Hands(min_detection_confidence=0.8, min_tracking_confidence=0.8)
draw = mediapipe.solutions.drawing_utils
wScr, hScr = autopy.screen.size()

# Initialize previous finger position and double tap flag
prev_finger_pos = None
double_tap_flag = False

def handLandmarks(colorImg):
    landmarkList = []
    landmarkPositions = mainHand.process(colorImg)
    landmarkCheck = landmarkPositions.multi_hand_landmarks
    if landmarkCheck:
        for hand in landmarkCheck:
            for landmark in hand.landmark:
                h, w, c = img.shape
                centerX, centerY = int(landmark.x * w), int(landmark.y * h)
                landmarkList.append([centerX, centerY])
    return landmarkList

def get_raised_fingers(finger_positions):
    raised_fingers = []
    if len(finger_positions) >= 5:  # Assuming at least 5 fingers are detected
        raised_fingers.append(1 if finger_positions[8] else 0)  # Pointer finger
        raised_fingers.append(1 if finger_positions[12] else 0)  # Middle finger
        raised_fingers.append(1 if finger_positions[16] else 0)  # Ring finger
        raised_fingers.append(1 if finger_positions[20] else 0)  # Small finger
    return raised_fingers

# Function to perform swipe action based on raised fingers
def perform_swipe(raised_fingers):
    if raised_fingers == [1, 0, 0, 0]:  # Pointer finger raised
        autopy.mouse.move(wScr - 5, autopy.mouse.location().y)  # Move cursor left
    elif raised_fingers == [1, 1, 0, 0]:  # Pointer and middle fingers raised
        autopy.mouse.move(wScr + 5, autopy.mouse.location().y)  # Move cursor right
    elif raised_fingers == [1, 1, 1, 0]:  # Pointer, middle, and ring fingers raised
        autopy.mouse.move(autopy.mouse.location().x, 5)  # Move cursor up
    elif raised_fingers == [1, 1, 1, 1]:  # All fingers raised
        autopy.mouse.click()  # Perform double click
    elif raised_fingers == [0, 0, 0, 0]:  # No fingers raised
        pass  # Do nothing
    else:
        autopy.mouse.move(autopy.mouse.location().x, hScr - 5)  # Move cursor down

while True:
    check, img = cap.read()
    imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    lmList = handLandmarks(imgRGB)

    if len(lmList) != 0:
        raised_fingers = get_raised_fingers(lmList)

        # Detecting double tap gesture
        if sum(len(hand) for hand in lmList) == 4 and not double_tap_flag:  # Assuming 4 hands for double tap
            double_tap_flag = True
            time.sleep(0.2)  # Adding a small delay to distinguish between single and double taps
        elif sum(len(hand) for hand in lmList) != 4 and double_tap_flag:
            double_tap_flag = False
        
        # Perform swipe action based on raised fingers
        perform_swipe(raised_fingers)

    cv2.imshow("Webcam", img)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

try:
    cap.release()
except:
    sys.exit()
cv2.destroyAllWindows()
