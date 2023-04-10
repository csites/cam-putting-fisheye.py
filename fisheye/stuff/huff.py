# Hough Line Transform Demo.
# Use this the with the Chessboard image to look a perspective camera corrections.

import cv2
import numpy as np


# Create a VideoCapture object to capture video from the default camera
cap = cv2.VideoCapture(0)

while True:
    # Read a frame from the video capture
    ret, frame = cap.read()

    # Convert the frame to grayscale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Apply Canny edge detection to find edges
    edges = cv2.Canny(gray, 50, 150, apertureSize=3)

    # Run the Hough Line Transform to find lines in the edges image
    lines = cv2.HoughLines(edges, rho=1, theta=np.pi/180, threshold=100)

    # Draw the detected lines on the original frame
    if lines is not None:
        for line in lines:
            rho, theta = line[0]
            a = np.cos(theta)
            b = np.sin(theta)
            x0 = a * rho
            y0 = b * rho
            x1 = int(x0 + 1000 * (-b))
            y1 = int(y0 + 1000 * (a))
            x2 = int(x0 - 1000 * (-b))
            y2 = int(y0 - 1000 * (a))
            cv2.line(frame, (x1, y1), (x2, y2), (0, 0, 255), 2)

    # Display the original frame with the detected lines
    cv2.imshow('frame', frame)

    # Check for the 'q' key to be pressed to exit the loop
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the VideoCapture object and close all windows
cap.release()
cv2.destroyAllWindows()
