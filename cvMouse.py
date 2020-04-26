import numpy as np
import cv2 as cv
import pyautogui
import time

pyautogui.FAILSAFE = False
cap = cv.VideoCapture(0)
initTime = time.time()

def setThreshold(frame, xyMatrix):
    rows, cols, _ = frame.shape

    y1 = int(cols * xyMatrix[0])
    y2 = int(cols * xyMatrix[1])
    x1 = int(rows * xyMatrix[2])
    x2 = int(rows * xyMatrix[3])

    frame = frame[x1:x2, y1:y2]

    blur = cv.GaussianBlur(frame, (5, 5), 0)
    greyFrame = cv.cvtColor(blur, cv.COLOR_BGR2GRAY)
    ret, thresh = cv.threshold(greyFrame, 0, 255, cv.THRESH_BINARY_INV+cv.THRESH_OTSU)
    thresh = cv.erode(thresh, None, iterations = 2)
    thresh = cv.dilate(thresh, None, iterations = 4)

    return thresh

def generateTrackpad(frame):
    contours, hierarchy = cv.findContours(frame.copy(), cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
    c = max(contours, key=cv.contourArea)
    extTop = tuple(c[c[:, :, 1].argmin()][0])

    colorFrame = cv.cvtColor(frame, cv.COLOR_GRAY2RGB)

    cols, rows, _ = colorFrame.shape

    trackpadFrameWidth = 192
    trackpadFrameHeight = 108

    trackpadTL = (int((rows - trackpadFrameWidth)/2), int((cols - trackpadFrameHeight)/2))
    trackpadBR = (int(rows - (rows - trackpadFrameWidth)/2), int(cols - (cols - trackpadFrameHeight)/2))
    
    cursorTL = (trackpadTL[0]-2, trackpadTL[1]-2)
    cursorBR = (trackpadTL[0]+2, trackpadTL[1]+2)

    cv.rectangle(colorFrame, trackpadTL, trackpadBR, (255, 0, 0), 3)

    if extTop[0] >= trackpadTL[0] and extTop[1] >= trackpadTL[1]:
        if extTop[0] <= trackpadBR[0] and extTop[1] <= trackpadBR[1]:
            cursorTL = (extTop[0]-2, extTop[1]-2)
            cursorBR = (extTop[0]+2, extTop[1]+2)
    
    cv.rectangle(colorFrame, cursorTL, cursorBR, (0, 0, 255), 2)

    cursorLoc = (10*((cursorTL[0]+2) - trackpadTL[0]), 10*((cursorTL[1]+2) - trackpadTL[1]))

    return colorFrame, cursorLoc

def generateBtn(frame):
    contours, hierarchy = cv.findContours(frame.copy(), cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
    c = max(contours, key=cv.contourArea)
    extRight = tuple(c[c[:, :, 0].argmax()][0])

    colorFrame = cv.cvtColor(frame, cv.COLOR_GRAY2RGB)

    cols, rows, _ = colorFrame.shape

    trackpadFrameWidth = 80
    trackpadFrameHeight = 80

    trackpadTL = (int((rows - trackpadFrameWidth)/2), int((cols - trackpadFrameHeight)/2))
    trackpadBR = (int(rows - (rows - trackpadFrameWidth)/2), int(cols - (cols - trackpadFrameHeight)/2))

    cv.rectangle(colorFrame, trackpadTL, trackpadBR, (255, 0, 255), 3)

    cursorTL = (trackpadTL[0]-2, trackpadTL[1]-2)
    cursorBR = (trackpadTL[0]+2, trackpadTL[1]+2)

    cursorClick = False
    cursorColorIndic = (0, 255, 0)

    if extRight[0] >= trackpadTL[0] and extRight[1] >= trackpadTL[1]:
        if extRight[0] <= trackpadBR[0] and extRight[1] <= trackpadBR[1]:
            cursorTL = (extRight[0]-2, extRight[1]-2)
            cursorBR = (extRight[0]+2, extRight[1]+2)
            cursorColorIndic = (0, 255, 0)
            cursorClick = True
    
    cv.rectangle(colorFrame, cursorTL, cursorBR, cursorColorIndic, 8)

    return colorFrame, cursorClick

def main():
    while(True):
        ret, frame = cap.read()
        currTime = time.time()

        image = cv.flip(frame, 90)
        trackpadXY = [0.6, 1.0, 0.2, 0.6]
        buttonXY = [0.7, 0.9, 0, 0.2]

        trackpadDisplay, cursorLoc  = generateTrackpad(setThreshold(image, trackpadXY))
        buttonDisplay, cursorClick = generateBtn(setThreshold(image, buttonXY))

        cv.imshow('Optical Trackpad', trackpadDisplay)
        cv.imshow('Optical Mouse Buttons', buttonDisplay)
        pyautogui.moveTo(cursorLoc[0], cursorLoc[1])

        if cursorClick and (currTime - initTime >= 4):
        	pyautogui.click()

        if cv.waitKey(1) & 0xFF == ord('q'):
            break

main()
cap.release()
cv.destroyAllWindows()