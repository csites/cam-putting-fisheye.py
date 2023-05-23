#
# Live video to allow image to pitch around the the center horizontal line (of the putting area to make 
# adjustments for perspective distortion.   This will refine the HLA and ball speed for any 
# shot that is not on the putting line center.
# keys: q=quit f=flip image u = toggle fisheye correction, p = toggle perspective correction, w = write pitch_angle to config.ini

import cv2
import numpy as np
import glob
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
osCFG_FILE='../config.ini'
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

# Read Perspective Correction angle from config.ini  
if parser.has_option('perspective', 'Camera_pitch'):
    pitch_angle=str2array(parser.get('perspective', 'Camera_pitch')) 
    P_test=1
else: 
    P_test=0
K_apply=0
flipImage=0
balance=1

def correct_perspective(image, pitch):
    global perspective_matrix
    height, width = image.shape[:2]
    center_line = int(height / 2)

    # Calculate the pitch in radians
    pitch_rad = np.radians(pitch)

    # Define the source and destination points for perspective transformation
    src_points = np.float32([[0, center_line], [width, center_line], [0, height], [width, height]])
    dst_points = np.float32([[0, center_line], [width, center_line], [width / 2 - np.tan(pitch_rad) * center_line, height],
                            [width / 2 + np.tan(pitch_rad) * center_line, height]])

    # Compute the perspective transformation matrix
    perspective_matrix = cv2.getPerspectiveTransform(src_points, dst_points)

    # Apply the perspective correction
    corrected_image = cv2.warpPerspective(image, perspective_matrix, (width, height))

    return corrected_image

def main():
    global K_test, K_apply, P_test, K, D, Scaled_K, pitch_angle, flipImage
    global balance
    
    camera_num = input("Enter camera number (0 to 4): ")
    try:
        camera_num = int(camera_num)
        if camera_num < 0 or camera_num > 3:
            raise ValueError("Camera number must be between 0-3")
    except ValueError:
        print("Invalid input. Please enter a number between 0-3.")
        exit()
    # create a VideoCapture object to capture video from the camera
    cap = cv2.VideoCapture(camera_num)

    width=int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height=int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    h1=round(height/2)
    wl=round(width/20)
    wr=width-wl
    w2=round(width/2)
  
    cv2.namedWindow('Output', cv2.WINDOW_NORMAL)
    if not P_test:
        pitch_angle = 0
    cv2.createTrackbar('Pitch', 'Output', pitch_angle, 90, lambda x: None)

    while True:
        key = cv2.waitKey(1)
        if key == ord('q'):
           break
        if key == ord('f'):
           if flipImage:
             flipImage=0
           else:
             flipImage=1
        if key == ord('u'):
           if K_apply:
             K_apply = 0
           else:
             K_apply = 1
        if key == ord('p'):
           if not P_test:
             P_test = 1
           else:
             P_test = 0
        if key == ord('w'):
            W_test = 0
            print("Write the pitch_angle to config.ini")
                          
        ret, img = cap.read()  # read a frame from the camera
        if not ret:
            break
            # This is how scaled_K, dim2 and balance are used to determine the final K used to un-distort image. OpenCV document failed to make this clear!
        if K_apply == 1:
            if K_test == 1:
              dim3 = dim2 = img.shape[:2][::-1]
              new_K = cv2.fisheye.estimateNewCameraMatrixForUndistortRectify(scaled_K, D, dim2, np.eye  (3), balance=balance)
              map1, map2 = cv2.fisheye.initUndistortRectifyMap(scaled_K, D, np.eye(3), new_K, dim3, cv2.CV_16SC2)
              img = cv2.remap(img, map1, map2, interpolation=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT)
    
        if flipImage == 1:
            img = cv2.flip(img, flipImage)
        if P_test == 1:
            pitch_angle = cv2.getTrackbarPos('Pitch', 'Output')
            img = correct_perspective(img, pitch_angle)

        img = cv2.line(img, (0,h1), (width,h1), (0,0,255), 1)
        img = cv2.line(img, (wl,0), (wl,height), (0,0,255), 1)
        img = cv2.line(img, (wr,0), (wr,height), (0,0,255), 1)
        img = cv2.line(img, (w2, h1-round(h1/10)), (w2, h1 + round(h1/10)), (0,0,255), 1)

        cv2.imshow('Output', img)
        # Create an entry in ../config.ini 

        if key == ord('w'):
            W_test = 0
            print("Write the pitch_angle to config.ini")
            # Note. This assume the application is one directory below where the config.ini is located.   
            config = configparser.ConfigParser()
            osFilename='config.ini'
            config.read(osFilename)
            if not config.has_section('perspective'):
                config.add_section('perspective')
            config.set('perspective', 'Camera_pitch', str(pitch_angle))
            with open(osFilename, 'w') as config_file:
                config.write(config_file)


    cv2.destroyAllWindows()

if __name__ == '__main__':
    main()
