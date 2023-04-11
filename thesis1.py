import cv2
import numpy as np
import thesis2 as htm
import time
import mouse
from pynput.mouse import Controller
from win32api import GetSystemMetrics

scroll = Controller()  # Module for mouse scrolling

delay = 0.3   # Mouse command delay
wCam, hCam = 640, 480 # Opencv frame resolution
frameR = 100  # Frame Reduction
smoothening = 7  # Reduce shaking of cursor

pTime = 0  # Previous time (to compute FPS)
plocX, plocY = 0, 0  # Previous x and y location
clocX, clocY = 0, 0  # Current x and y location

cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)  # Set default camera
cap.set(3, wCam)  # Set camera width
cap.set(4, hCam)  # Set camera height
detector = htm.handDetector(maxHands=1)  # Only allow detecting 1 hand
wScr, hScr = GetSystemMetrics(0), GetSystemMetrics(1)  # Get device resolution

while True:
    # Find hand Landmarks
    success, img = cap.read()
    img = detector.findHands(img)
    lmList, bbox = detector.findPosition(img)

    # Get the tip of the index and middle finger
    if len(lmList) != 0:
        x1, y1 = lmList[8][1:3]  # Index Finger
        x2, y2 = lmList[12][1:3]  # Middle Finger

    # Check which fingers are up
    fingers = detector.fingersUp()

    # Place rectangle on the window to serve as a guide for the device's screen
    cv2.rectangle(img, (frameR, frameR), (wCam - frameR, hCam - frameR), (0, 255, 0), 2)

    # MOVE CURSOR - only index finger is up
    if fingers[1] == 1 and fingers[2] == 0 and fingers[3] == 0 and fingers[4] == 0:
        # Convert Coordinates
        x3 = np.interp(x1, (frameR, wCam - frameR), (0, wScr))
        y3 = np.interp(y1, (frameR, hCam - frameR), (0, hScr))

        # Smoothen Values
        clocX = plocX + (x3 - plocX) / smoothening
        clocY = plocY + (y3 - plocY) / smoothening
        print(f"Distance (MOVE MOUSE):")
        print(f"x = {x3}")
        print(f"y = {y3} \n")

        # Move
        mouse.move(wScr - clocX, clocY)
        plocX, plocY = clocX, clocY

    # HOLD - Index and Middle finger is up
    if fingers[1] == 1 and fingers[2] == 1 and fingers[3] == 0 and fingers[4] == 0:
        # Find distance between index and middle finger
        distance, img, lineInfo = detector.findDistance(8, 12, img)
        print(f"Distance (HOLD): {distance}")

        # Hold left click if index and middle finger touches
        if distance < distance + 1:
            mouse.press('left')

            x3 = np.interp(x1, (frameR, wCam - frameR), (0, wScr))
            y3 = np.interp(y1, (frameR, hCam - frameR), (0, hScr))

            # Smoothen Values
            clocX = plocX + (x3 - plocX) / smoothening
            clocY = plocY + (y3 - plocY) / smoothening

            # Move
            mouse.move(wScr - clocX, clocY)
            cv2.circle(img, (x1, y1), 15, (0, 0, 0), cv2.FILLED)
            plocX, plocY = clocX, clocY

        # Release left click
        if distance > (distance // 3.1) + 39:
            mouse.release('left')

    # LEFT CLICK - only the thumb is up
    elif fingers[0] == 1 and fingers[1] == 0 and fingers[2] == 0 and fingers[3] == 0 and fingers[4] == 0:
        # Find distance of point 4 (tip of thumb) and point 1
        distanceLeft, img, lineInfo = detector.findDistance(4, 1, img)
        print(f"Distance (LEFT CLICK): {distanceLeft}")
        mouse.click(button='left')
        time.sleep(delay)

    # RIGHT CLICK - only pinky finger is up
    elif fingers[1] == 0 and fingers[2] == 0 and fingers[3] == 0 and fingers[4] == 1:
        # Find distance of point 20 (tip of pinky) and point 17
        distanceRight, img, lineInfo = detector.findDistance(20, 17, img)
        print(f"Distance (RIGHT CLICK): {distanceRight}")
        mouse.click(button='right')
        time.sleep(delay)

    # DOUBLE CLICK - middle, ring, and pinky finger is up
    elif fingers[1] == 0 and fingers[2] == 1 and fingers[3] == 1 and fingers[4] == 1:
        # Find distance of thumb and index finger
        distanceClick, img, lineInfo = detector.findDistance(4, 8, img)

        # Double click if thumb and index finger touches
        if distanceClick < distanceClick + 1:
            print(f"Distance (DOUBLE CLICK): {distanceClick}")
            mouse.double_click(button='left')
            time.sleep(delay)

    # SCROLL UP - index, ring, and pinky finger is up
    elif fingers[1] == 1 and fingers[2] == 0 and fingers[3] == 1 and fingers[4] == 1:
        # Find distance of thumb and middle finger
        distanceUp, img, lineInfo = detector.findDistance(4, 12, img)

        # Scroll up if thumb and middle finger touches
        if distanceUp < distanceUp + 1:
            print(f"Distance (Scroll Up): {distanceUp}")
            scroll.scroll(0, 3)
            time.sleep(delay)


    # SCROLL DOWN - index, middle, and pinky finger is up
    elif fingers[1] == 1 and fingers[2] == 1 and fingers[3] == 0 and fingers[4] == 1:
        # Find distance thumb and ring finger
        distanceDown, img, lineInfo = detector.findDistance(4, 16, img)

        # Double click if thumb and ring finger touches
        if distanceDown < distanceDown + 1:
            print(f"Distance (Scroll Down): {distanceDown}")
            scroll.scroll(0, -3)
            time.sleep(delay)

    # Frame Rate
    # cTime = time.time()
    # fps = 1 / (cTime - pTime)
    # pTime = cTime
    # cv2.putText(img, "FPS: " + str(int(fps)), (20, 50), cv2.FONT_HERSHEY_PLAIN, 2, (0, 255, 0), 2)

    # Display
    cv2.imshow("Virtual Mouse", img)
    k = cv2.waitKey(1)
    if k == 27:  # wait for ESC key to exit program
        break