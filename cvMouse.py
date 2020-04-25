import numpy as np
import cv2 as cv
import pyautogui

pyautogui.FAILSAFE = False
cap = cv.VideoCapture(0)

def setThreshold(frame):
    rows, cols, _ = frame.shape

    y1 = int(cols * 0.60)
    y2 = int(cols)
    x1 = int(rows * 0.20)
    x2 = int(rows * 0.60)

    frame = frame[x1:x2, y1:y2]

    blur = cv.GaussianBlur(frame, (5, 5), 0)
    greyFrame = cv.cvtColor(blur, cv.COLOR_BGR2GRAY)
    ret, thresh = cv.threshold(greyFrame, 0, 255, cv.THRESH_BINARY_INV+cv.THRESH_OTSU)
    thresh = cv.erode(thresh, None, iterations = 2)
    thresh = cv.dilate(thresh, None, iterations = 4)

    return thresh

def fingerDetect(frame):
    contours, hierarchy = cv.findContours(frame.copy(), cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
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
        else:
            cursorTL = (trackpadBR[0]-2, trackpadBR[1]-2)
            cursorBR = (trackpadBR[0]+2, trackpadBR[1]+2)
    else:
        cursorTL = (trackpadTL[0]-2, trackpadTL[1]-2)
        cursorBR = (trackpadTL[0]+2, trackpadTL[1]+2)
    
    cv.rectangle(colorFrame, cursorTL, cursorBR, (0, 255, 0), 2)

    cursorLoc = (10*((cursorTL[0]+2) - trackpadTL[0]), 10*((cursorTL[1]+2) - trackpadTL[1]))

    return colorFrame, cursorLoc

def main():
    while(True):
        ret, frame = cap.read()

        image = cv.flip(frame, 90)

        trackpadDisplay, cursorLoc = fingerDetect(setThreshold(image))

        cv.imshow('Optical Trackpad v 0.1b', trackpadDisplay)
        pyautogui.moveTo(cursorLoc[0], cursorLoc[1])

        if cv.waitKey(1) & 0xFF == ord('q'):
            break

main()
cap.release()
cv.destroyAllWindows()