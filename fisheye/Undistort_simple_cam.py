#
# Simple capture and undistort image, and show alignment.
import cv2
assert cv2.__version__[0] >= '3', 'The fisheye module requires opencv version >= 3.0.0'
import numpy as np
import os
import re
import ast

from configparser import ConfigParser

def str2array(s):
    # Remove space after [
    s=re.sub('\[ +', '[', s.strip())
    # Replace commas and spaces
    s=re.sub('[,\s]+', ', ', s)
    return np.array(ast.literal_eval(s))

parser = ConfigParser()
osCFG_FILE='config.ini'
parser.read(osCFG_FILE)

# Read Fisheye len correction matrixes from config.ini  
if parser.has_option('fisheye', 'k'):
    K=str2array(parser.get('fisheye', 'k')) 
    K_test=1
else: 
    K_test=0

if parser.has_option('fisheye', 'd'):
    D=str2array(parser.get('fisheye', 'd'))
if parser.has_option('fisheye', 'scaled_k'):
    scaled_K=str2array(parser.get('fisheye', 'scaled_k'))

camera_num = input("Enter camera number (0 to 4): ")

try:
    camera_num = int(camera_num)
    if camera_num < 0 or camera_num > 4:
        raise ValueError("Camera number must be between 0-4")
except ValueError:
    print("Invalid input. Please enter a number between 0-4.")
    exit()

# create a VideoCapture object to capture video from the camera

cap = cv2.VideoCapture(camera_num)

# cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
# cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
# showing values of the properties
width=int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height=int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
print("CV_CAP_PROP_FRAME_WIDTH: '{}'".format(cap.get(cv2.CAP_PROP_FRAME_WIDTH)))
print("CV_CAP_PROP_FRAME_HEIGHT : '{}'".format(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)))
print("CAP_PROP_FPS : '{}'".format(cap.get(cv2.CAP_PROP_FPS)))
print("CAP_PROP_POS_MSEC : '{}'".format(cap.get(cv2.CAP_PROP_POS_MSEC)))
print("CAP_PROP_FRAME_COUNT : '{}'".format(cap.get(cv2.CAP_PROP_FRAME_COUNT)))
print("CAP_PROP_BRIGHTNESS : '{}'".format(cap.get(cv2.CAP_PROP_BRIGHTNESS)))
print("CAP_PROP_CONTRAST : '{}'".format(cap.get(cv2.CAP_PROP_CONTRAST)))
print("CAP_PROP_SATURATION : '{}'".format(cap.get(cv2.CAP_PROP_SATURATION)))
print("CAP_PROP_HUE : '{}'".format(cap.get(cv2.CAP_PROP_HUE)))
print("CAP_PROP_GAIN : '{}'".format(cap.get(cv2.CAP_PROP_GAIN)))
print("CAP_PROP_CONVERT_RGB : '{}'".format(cap.get(cv2.CAP_PROP_CONVERT_RGB)))
print(width) 
print(height)
# For allignment, it might be usefull to flip the image to make camera adjustments more intuitive 
# make left camera direction left in the camera image, right direction right in the camera image.
flipImage=0

h1=round(height/2)
wl=round(width/20)
wr=width-wl
w2=round(width/2)

balance=1

# capture video from the camera
while True:
    key=cv2.waitKey(1)
    if key == ord('q'):
      break
    if key == ord('f'):
       if flipImage:
         flipImage=0
       else:
         flipImage=1
     
    ret, img = cap.read()  # read a frame from the camera
    if not ret:
        break
        # This is how scaled_K, dim2 and balance are used to determine the final K used to un-distort image. OpenCV document failed to make this clear!
    if K_test == 1:
        dim3 = dim2 = img.shape[:2][::-1]
        new_K = cv2.fisheye.estimateNewCameraMatrixForUndistortRectify(scaled_K, D, dim2, np.eye  (3), balance=balance)
        map1, map2 = cv2.fisheye.initUndistortRectifyMap(scaled_K, D, np.eye(3), new_K, dim3, cv2.CV_16SC2)
        img = cv2.remap(img, map1, map2, interpolation=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT)

    img = cv2.line(img, (0,h1), (width,h1), (0,0,255), 1)
    img = cv2.line(img, (wl,0), (wl,height), (0,0,255), 1)
    img = cv2.line(img, (wr,0), (wr,height), (0,0,255), 1)
    img = cv2.line(img, (w2, h1-round(h1/10)), (w2, h1 + round(h1/10)), (0,0,255), 1)
    if flipImage == 1:
       img = cv2.flip(img, flipImage)
    cv2.imshow('Camera f=flip, q=quit', img)  # display the frame
    

# release the camera and close the window
cap.release()
cv2.destroyAllWindows()
