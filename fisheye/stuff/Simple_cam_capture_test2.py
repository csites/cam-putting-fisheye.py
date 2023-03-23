#
# Camera_capture test 2
# Simple capture test.
import cv2

# create a VideoCapture object to capture video from the camera
cap = cv2.VideoCapture(0, cv2.CAP_DSHOW) 

# set the video stream type to MJPG
cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))

# set the frame size (width, height) in pixels
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

# set the frame rate (frames per second)
cap.set(cv2.CAP_PROP_FPS, 120)

# capture video from the camera
while True:
    ret, frame = cap.read()  # read a frame from the camera
    if not ret:
        break
    cv2.imshow('Camera', frame)  # display the frame
    if cv2.waitKey(1) == ord('q'):  # press q to quit
        break

# release the camera and close the window
cap.release()
cv2.destroyAllWindows()
