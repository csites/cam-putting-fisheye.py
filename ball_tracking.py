# import the necessary packages
from collections import deque
import numpy as np
import argparse
import cv2
import imutils
import time
import sys
import cvzone
from ColorModuleExtended import ColorFinder
import math
from decimal import *
import requests
from configparser import ConfigParser
import ast
import re

def str2array(s):
    # Remove space after [
    s=re.sub('\[ +', '[', s.strip())
    # Replace commas and spaces
    s=re.sub('[,\s]+', ', ', s)
    return np.array(ast.literal_eval(s),dtype=np.float64)

parser = ConfigParser()
CFG_FILE = 'config.ini'
parser.read(CFG_FILE)

# Startpoint Zone
ballradius = 0
darkness = 0
flipImage = 0
mjpegenabled = 0
ps4=0
overwriteFPS = 0
customhsv = {}

if parser.has_option('putting', 'startx1'):
    sx1=int(parser.get('putting', 'startx1'))
else:
    sx1=10
if parser.has_option('putting', 'startx2'):
    sx2=int(parser.get('putting', 'startx2'))
else:
    sx2=180
if parser.has_option('putting', 'y1'):
    y1=int(parser.get('putting', 'y1'))
else:
    y1=180
if parser.has_option('putting', 'y2'):
    y2=int(parser.get('putting', 'y2'))
else:
    y2=450
if parser.has_option('putting', 'radius'):
    ballradius=int(parser.get('putting', 'radius'))
else:
    ballradius=0
if parser.has_option('putting', 'flip'):
    flipImage=int(parser.get('putting', 'flip'))
else:
    flipImage=0
if parser.has_option('putting', 'darkness'):
    darkness=int(parser.get('putting', 'darkness'))
else:
    darkness=0
if parser.has_option('putting', 'mjpeg'):
    mjpegenabled=int(parser.get('putting', 'mjpeg'))
else:
    mjpegenabled=0
if parser.has_option('putting', 'ps4'):
    ps4=int(parser.get('putting', 'ps4'))
else:
    ps4=0
if parser.has_option('putting', 'fps'):
    overwriteFPS=int(parser.get('putting', 'fps'))
else:
    overwriteFPS=0
if parser.has_option('putting', 'height'):
    height=int(parser.get('putting', 'height'))
else:
    height=360
if parser.has_option('putting', 'width'):
    width=int(parser.get('putting', 'width'))
else:
    width=640
if parser.has_option('putting', 'customhsv'):
    customhsv=ast.literal_eval(parser.get('putting', 'customhsv'))
    print(customhsv)
else:
    customhsv={}
    
# Local stimp correction factor.   [0.0 to 2.0] 1.0 = default. 
if parser.has_option('Stimp_Adjust', 'stimp'):
    stimp=float(parser.get('Stimp_Adjust', 'stimp'))
    istimp=int(stimp * 100.0)
else:
    stimp=100.0
    istimp=100
    
# Read Fisheye len correction matrixes from config.ini  
if parser.has_option('fisheye', 'k'):
    K=str2array(parser.get('fisheye', 'k')) 
    print(K)
    K_test=1
else: 
    K_test=0
if parser.has_option('fisheye', 'd'):
    D=str2array(parser.get('fisheye', 'd'))
    print(D)
if parser.has_option('fisheye', 'scaled_k'):
    scaled_K=str2array(parser.get('fisheye', 'scaled_k'))
    print(scaled_K)
# Camera properties Exposure: -7 means 2^-7 = 1/(2^7) = 1/128 sec.  A value of -1 = 2^(-1) = 1/(2^1) = 1/2 sec exposure time or 2FPS.
if parser.has_option('camera_properties','exposure'):
    cam_exposure=float(parser.get('camera_properties','exposure'))
else:
    cam_exposure=0.0
# CAP_PROP_AUTO_EXPOSURE is 0.25 this means manual, 0.75 sets it to automatic (default). *workaround bug*    
if parser.has_option('camera_properties','auto_exposure'):
    cam_autoexposure=float(parser.get('camera_properties','auto_exposure'))
else:
    cam_autoexposure=0.0
if parser.has_option('camera_properties','brightness'):
    cam_brightness=float(parser.get('camera_properties','brightness'))
else:
    cam_brightness=0.0    
if parser.has_option('camera_properties','contrast'):
    cam_contrast=float(parser.get('camera_properties','contrast'))
else:
    cam_contrast=0.0
if parser.has_option('camera_properties','hue'):
    cam_hue=float(parser.get('camera_properties','hue'))
else:
    cam_hue=0.0    
if parser.has_option('camera_properties','gamma'):
    cam_gamma=float(parser.get('camera_properties','gamma'))
else:
    cam_gamma=0.0
if parser.has_option('camera_properties','gain'):
    cam_gain=float(parser.get('camera_properties','gain'))
else:
    cam_gain=0.0
if parser.has_option('camera_properties','saturation'):
    cam_saturation=float(parser.get('camera_properties','saturation'))
else:
    cam_saturation=0.0
if parser.has_option('camera_properties','webcamindex'):
    cam_webcamindex=int(parser.get('camera_properties','webcamindex'))
else:
    cam_webcamindex=0
# Read Perspective Correction angle from config.ini  
if parser.has_option('perspective', 'Camera_pitch'):
    camera_pitch=int(parser.get('perspective', 'Camera_pitch')) 
    P_test=1
else: 
    P_test=0
if parser.has_option('perspective', 'Putt_line'):
    putt_line=int(parser.get('perspective', 'Putt_line'))
else: 
    putt_line = -1
    

# Detection Gateway
x1=sx2+10
x2=x1+10

#coord of polygon in frame::: [[x1,y1],[x2,y2],[x3,y3],[x4,y4]]
startcoord=[[sx1,y1],[sx2,y1],[sx1,y2],[sx2,y2]]

#coord of polygon in frame::: [[x1,y1],[x2,y2],[x3,y3],[x4,y4]]
coord=[[x1,y1],[x2,y1],[x1,y2],[x2,y2]]

golfballradius = 21.33; # in mm

actualFPS = 0

videoStartTime = time.time()

# initialize variables to store the start and end positions of the ball
startCircle = (0, 0, 0)
endCircle = (0, 0, 0)
startPos = (0,0)
endPos = (0,0)
startTime = time.time()
pixelmmratio = 0

# initialize variable to store start candidates of balls
startCandidates = []
startminimum = 30

# Initialize Entered indicator
entered = False
started = False
left = False

lastShotStart = (0,0)
lastShotEnd = (0,0)
lastShotSpeed = 0
lastShotHLA = 0 

speed = 0
lspeed0 = 0
tim1 = 0
tim2 = 0

# calibration

colorcount = 0
calibrationtime = time.time()
calObjectCount = 0
calColorObjectCount = []
calibrationTimeFrame = 30

# Calibrate Recording Indicator

record = True

# Videofile Indicator

videofile = False

# a_key_pressed (remove duplicate advanced screens for multipla 'a' and 's' key presses)
a_key_pressed = False 
s_key_pressed = False
# For fisheye camera undistorted video frame.  Balance for the undistort video
undistort_video = False
flip_video = False
balance=1 

# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-v", "--video",
                help="path to the (optional) video file")
ap.add_argument("-i", "--img",
                help="path to the (optional) image file")
ap.add_argument("-b", "--buffer", type=int, default=64,
                help="max buffer size - default is 64")
ap.add_argument("-w", "--camera", type=int, default=0,
                help="webcam index number - default is 0")
ap.add_argument("-c", "--ballcolor",
                help="ball color - default is yellow")
ap.add_argument("-d", "--debug",
                help="debug - color finder and wait timer")
ap.add_argument("-r", "--resize", type=int, default=640,
                help="window resize in width pixel - default is 640px")
args = vars(ap.parse_args())

# define the lower and upper boundaries of the different ball color options (-c)
# ball in the HSV color space, then initialize the

#red                   
red = {'hmin': 1, 'smin': 208, 'vmin': 0, 'hmax': 50, 'smax': 255, 'vmax': 249} # light
red2 = {'hmin': 1, 'smin': 240, 'vmin': 61, 'hmax': 50, 'smax': 255, 'vmax': 249} # dark

#white
white = {'hmin': 168, 'smin': 218, 'vmin': 118, 'hmax': 179, 'smax': 247, 'vmax': 216} # very light
white2 = {'hmin': 159, 'smin': 217, 'vmin': 152, 'hmax': 179, 'smax': 255, 'vmax': 255} # light
white3 = {'hmin': 0, 'smin': 181, 'vmin': 0, 'hmax': 42, 'smax': 255, 'vmax': 255}

#yellow

yellow = {'hmin': 0, 'smin': 210, 'vmin': 0, 'hmax': 15, 'smax': 255, 'vmax': 255} # light
yellow2 = {'hmin': 0, 'smin': 150, 'vmin': 100, 'hmax': 46, 'smax': 255, 'vmax': 206} # dark

#green
green = {'hmin': 0, 'smin': 169, 'vmin': 161, 'hmax': 177, 'smax': 204, 'vmax': 255} # light
green2 = {'hmin': 0, 'smin': 109, 'vmin': 74, 'hmax': 81, 'smax': 193, 'vmax': 117} # dark

#orange
orange = {'hmin': 0, 'smin': 219, 'vmin': 147, 'hmax': 19, 'smax': 255, 'vmax': 255}# light
orange2 = {'hmin': 3, 'smin': 181, 'vmin': 134, 'hmax': 40, 'smax': 255, 'vmax': 255}# dark
orange3 = {'hmin': 0, 'smin': 73, 'vmin': 150, 'hmax': 40, 'smax': 255, 'vmax': 255}# test
orange4 = {'hmin': 3, 'smin': 181, 'vmin': 216, 'hmax': 40, 'smax': 255, 'vmax': 255}# ps3eye

calibrate = {}

# for Colorpicker
# default yellow option
hsvVals = yellow

if customhsv == {}:

    if args.get("ballcolor", False):
        if args["ballcolor"] == "white":
            hsvVals = white
        elif args["ballcolor"] == "white2":
            hsvVals = white2
        elif args["ballcolor"] ==  "yellow":
            hsvVals = yellow 
        elif args["ballcolor"] ==  "yellow2":
            hsvVals = yellow2 
        elif args["ballcolor"] ==  "orange":
            hsvVals = orange
        elif args["ballcolor"] ==  "orange2":
            hsvVals = orange2
        elif args["ballcolor"] ==  "orange3":
            hsvVals = orange3
        elif args["ballcolor"] ==  "orange4":
            hsvVals = orange4
        elif args["ballcolor"] ==  "green":
            hsvVals = green 
        elif args["ballcolor"] ==  "green2":
            hsvVals = green2               
        elif args["ballcolor"] ==  "red":
            hsvVals = red             
        elif args["ballcolor"] ==  "red2":
            hsvVals = red2             
        else:
            hsvVals = yellow

        if args["ballcolor"] is not None:
            print("Ballcolor: "+str(args["ballcolor"]))
else:
    hsvVals = customhsv
    print("Custom HSV Values set in config.ini")



    
calibrationcolor = [("white",white),("white2",white2),("yellow",yellow),("yellow2",yellow2),("orange",orange),("orange2",orange2),("orange3",orange3),("orange4",orange4),("green",green),("green2",green2),("red",red),("red2",red2)]

def resizeWithAspectRatio(image, width=None, height=None, inter=cv2.INTER_AREA):
    dim = None
    (h, w) = image.shape[:2]

    if width is None and height is None:
        return image
    if width is None:
        r = height / float(h)
        dim = (int(w * r), height)
    else:
        r = width / float(w)
        dim = (width, int(h * r))

    return cv2.resize(image, dim, interpolation=inter)


# Start Splash Screen

frame = cv2.imread("error.png")
cv2.putText(frame,"Starting Video: Try MJPEG option in advanced settings for faster startup",(20,100),cv2.FONT_HERSHEY_SIMPLEX,0.5,(0, 0, 255))
outputframe = resizeWithAspectRatio(frame, width=int(args["resize"]))
cv2.imshow("Putting View: Press q to exit / a for adv. settings", outputframe)

# Create the color Finder object set to True if you need to Find the color

if args.get("debug", False):
    myColorFinder = ColorFinder(True)
    myColorFinder.setTrackbarValues(hsvVals)
else:
    myColorFinder = ColorFinder(False)

pts = deque(maxlen=args["buffer"])
tims = deque(maxlen=args["buffer"])
fpsqueue = deque(maxlen=240)

# Initialize variables as needed.
webcamindex = 0

message = ""


# if a webcam index is supplied, grab the reference
if args.get("camera", False):
    webcamindex = args["camera"]

# if a video path was not supplied, grab the reference
# to the webcam
if not args.get("video", False):
    webcamindex = cam_webcamindex 
    if mjpegenabled == 0:
        vs = cv2.VideoCapture(webcamindex + cv2.CAP_DSHOW)
    else:
        vs = cv2.VideoCapture(webcamindex + cv2.CAP_DSHOW)
        # Check if FPS is overwritten in config
        if overwriteFPS != 0:
            vs.set(cv2.CAP_PROP_FPS, overwriteFPS)
            print("Overwrite FPS: "+str(vs.get(cv2.CAP_PROP_FPS)))
        if height != 0 and width != 0:
            vs.set(cv2.CAP_PROP_FRAME_WIDTH, width)
            vs.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
        mjpeg = cv2.VideoWriter_fourcc('M','J','P','G')
        vs.set(cv2.CAP_PROP_FOURCC, mjpeg)
    if vs.get(cv2.CAP_PROP_BACKEND) == -1:
        message = "No Camera could be opened at webcamera index "+str(webcamindex)+". If your webcam only supports compressed format MJPEG instead of YUY2 please set MJPEG option to 1"
    else:
        if ps4 == 1:
            #cap.set(cv2.CAP_PROP_FRAME_WIDTH, 3448)
            #cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 808)
            vs.set(cv2.CAP_PROP_FRAME_WIDTH, 1724)
            vs.set(cv2.CAP_PROP_FRAME_HEIGHT, 404)
            #vs.set(cv2.CAP_PROP_FPS, 120)
        print("Backend: "+str(vs.get(cv2.CAP_PROP_BACKEND)))
        print("FourCC: "+str(vs.get(cv2.CAP_PROP_FOURCC)))
        print("FPS: "+str(vs.get(cv2.CAP_PROP_FPS)))
else:
    vs = cv2.VideoCapture(args["video"])
    videofile = True

# Set all the odd camera options
if parser.has_option('camera_properties','brightness'):
    vs.set(cv2.CAP_PROP_BRIGHTNESS, cam_brightness )
if parser.has_option('camera_properties','contrast'):
    vs.set(cv2.CAP_PROP_CONTRAST, cam_contrast)
if parser.has_option('camera_properties','hue'):
    vs.set(cv2.CAP_PROP_HUE, cam_hue)
if parser.has_option('camera_properties','saturation'):    
    vs.set(cv2.CAP_PROP_SATURATION, cam_saturation)
if parser.has_option('camera_properties','exposure'):
    vs.set(cv2.CAP_PROP_EXPOSURE, cam_exposure)  # -7 means 2^-7 = 1/(2^7) = 1/128 sec.  A value of -1 = 2^(-1) = 1/(2^1) = 1/2 sec exposure time or 2FPS.    
if parser.has_option('camera_properties','auto_exposure'):
    if cam_autoexposure == -1:
        cam_autoexposure = 0.75
    if cam_autoexposure == 0:
        cam_autoexposure = 0.25
    vs.set(cv2.CAP_PROP_AUTO_EXPOSURE, cam_autoexposure) # CAP_PROP_AUTO_EXPOSURE is 0.25 this means manual, 0.75 sets it to automatic *workaround bug*
if parser.has_option('camera_properties','gamma'):
    vs.set(cv2.CAP_PROP_GAMMA, cam_gamma)
if parser.has_option('camera_properties','gain'):
    vs.set(cv2.CAP_PROP_GAIN, cam_gain)

# Get video metadata
video_fps = vs.get(cv2.CAP_PROP_FPS)
height = vs.get(cv2.CAP_PROP_FRAME_HEIGHT)
width = vs.get(cv2.CAP_PROP_FRAME_WIDTH)
brightness = vs.get(cv2.CAP_PROP_BRIGHTNESS)
contrast = vs.get(cv2.CAP_PROP_CONTRAST)
hue = vs.get(cv2.CAP_PROP_HUE)
saturation = vs.get(cv2.CAP_PROP_SATURATION)
exposure = vs.get(cv2.CAP_PROP_EXPOSURE)  # -7 means 2^-7 = 1/(2^7) = 1/128 sec.  A value of -1 = 2^(-1) = 1/(2^1) = 1/2 sec exposure time or 2FPS.    
auto_exposure = vs.get(cv2.CAP_PROP_AUTO_EXPOSURE) # CAP_PROP_AUTO_EXPOSURE is 0.25 this means manual, 0.75 sets it to automatic *workaround bug*
gamma = vs.get(cv2.CAP_PROP_GAMMA)
gain = vs.get(cv2.CAP_PROP_GAIN)

print("video_fps: "+str(video_fps))
print("height: "+str(height))
print("width: "+str(width))
print("brightness: "+str(brightness))
print("contrast: "+str(contrast))
print("hue: "+str(hue))
print("saturation: "+str(saturation))
print("exposure: "+str(exposure))
print("auto_exposure: "+str(auto_exposure))
print("gamma: "+str(gamma))
print("gain: "+str(gain))

if type(video_fps) == float:
    if video_fps == 0.0:
        e = vs.set(cv2.CAP_PROP_FPS, 60)
        new_fps = []
        new_fps.append(0)

    if video_fps > 0.0:
        new_fps = []
        new_fps.append(video_fps)
    video_fps = new_fps

# Setup the perspective matrix P_matrix if we are doing perspective correction.
if P_test == 1:
    if putt_line == -1:
        putt_line = int(height / 2)
    # Calculate the pitch in radians
    pitch_rad = np.radians(camera_pitch)
    # Define the source and destination points for perspective transformation
    src_points = np.float32([[0, putt_line], [width, putt_line], [0, height], [width, height]])
    dst_points = np.float32([[0, putt_line], [width, putt_line], [width / 2 - np.tan(pitch_rad) * putt_line, height],
                            [width / 2 + np.tan(pitch_rad) * putt_line, height]])
    # Compute the perspective transformation matrix
    pmatrix = cv2.getPerspectiveTransform(src_points, dst_points)

# we are using x264 codec for mp4
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
#out1 = cv2.VideoWriter('Ball-New.mp4', apiPreference=0, fourcc=fourcc,fps=video_fps[0], frameSize=(int(width), int(height)))
out2 = cv2.VideoWriter('Calibration.mp4', apiPreference=0, fourcc=fourcc,fps=120, frameSize=(int(width), int(height)))


def decode(frame):
    left = np.zeros((400,632,3), np.uint8)
    right = np.zeros((400,632,3), np.uint8)
    
    for i in range(400):
        left[i] = frame[i, 32: 640 + 24] 
        right[i] = frame[i, 640 + 24: 640 + 24 + 632] 
    
    return (left, right)

# Fix this for efficency please.
def correct_perspective_image(image):
    global pmatrix, width, height
    # Apply the perspective correction
    corrected_image = cv2.warpPerspective(image, pmatrix, (int(width), int(height)))
    return corrected_image

def correct_perspective_point(p):
    global pmatrix
    px = (pmatrix[0][0]*p[0] + pmatrix[0][1]*p[1] + pmatrix[0][2]) / ((pmatrix[2][0]*p[0] + pmatrix[2][1]*p[1] + pmatrix[2][2]))
    py = (pmatrix[1][0]*p[0] + pmatrix[1][1]*p[1] + pmatrix[1][2]) / ((pmatrix[2][0]*p[0] + pmatrix[2][1]*p[1] + pmatrix[2][2]))
    p_after = (int(px), int(py))
    return p_after
    
def setFPS(value):
    print(value)
    vs.set(cv2.CAP_PROP_FPS,value)
    pass 

def setXStart(value):
    print(value)
    startcoord[0][0]=value
    startcoord[2][0]=value

    global sx1
    sx1=int(value)    
    parser.set('putting', 'startx1', str(sx1))
    parser.write(open(CFG_FILE, "w"))
    pass

def setXEnd(value):
    print(value)
    startcoord[1][0]=value
    startcoord[3][0]=value 

    global x1
    global x2
    global sx2
     
    # Detection Gateway
    x1=int(value+10)
    x2=int(x1+10)

    #coord=[[x1,y1],[x2,y1],[x1,y2],[x2,y2]]
    coord[0][0]=x1
    coord[2][0]=x1
    coord[1][0]=x2
    coord[3][0]=x2

    sx2=int(value)    
    parser.set('putting', 'startx2', str(sx2))
    parser.write(open(CFG_FILE, "w"))
    pass  

def setYStart(value):
    print(value)
    startcoord[0][1]=value
    startcoord[1][1]=value

    global y1

    #coord=[[x1,y1],[x2,y1],[x1,y2],[x2,y2]]
    coord[0][1]=value   
    coord[1][1]=value

    y1=int(value)    
    parser.set('putting', 'y1', str(y1))
    parser.write(open(CFG_FILE, "w"))     
    pass


def setYEnd(value):
    print(value)
    startcoord[2][1]=value
    startcoord[3][1]=value 

    global y2

    #coord=[[x1,y1],[x2,y1],[x1,y2],[x2,y2]]
    coord[2][1]=value   
    coord[3][1]=value

    y2=int(value)    
    parser.set('putting', 'y2', str(y2))
    parser.write(open(CFG_FILE, "w"))     
    pass 

def setBallRadius(value):
    print(value)    
    global ballradius
    ballradius = int(value)
    parser.set('putting', 'radius', str(ballradius))
    parser.write(open(CFG_FILE, "w"))
    pass

def setFlip(value):
    print(value)    
    global flipImage
    flipImage = int(value)
    parser.set('putting', 'flip', str(flipImage))
    parser.write(open(CFG_FILE, "w"))
    pass

def setMjpeg(value):
    print(value)    
    global mjpegenabled
    global message
    if mjpegenabled != int(value):
        vs.release()
        message = "Video Codec changed - Please restart the putting app"
    mjpegenabled = int(value)
    parser.set('putting', 'mjpeg', str(mjpegenabled))
    parser.write(open(CFG_FILE, "w"))
    pass

def setOverwriteFPS(value):
    print(value)    
    global overwriteFPS
    global message
    if overwriteFPS != int(value):
        vs.release()
        message = "Overwrite of FPS changed - Please restart the putting app"
    overwriteFPS = int(value)
    parser.set('putting', 'fps', str(overwriteFPS))
    parser.write(open(CFG_FILE, "w"))
    pass

def setDarkness(value):
    print(value)    
    global darkness
    darkness = int(value)
    parser.set('putting', 'darkness', str(darkness))
    parser.write(open(CFG_FILE, "w"))
    pass    

def setStimp(value):
    print(value)    
    global stimp
    stimp = float(value)/100.0
    if not parser.has_section('Stimp_Adjust'):
      parser.add_section('Stimp_Adjust')
    parser.set('Stimp_Adjust', 'stimp', str(stimp))
    parser.write(open(CFG_FILE, "w"))
    pass    

def GetAngle (p1, p2):
    x1, y1 = p1
    x2, y2 = p2
    dX = x2 - x1
    dY = y2 - y1
    rads = math.atan2 (-dY, dX)

    if flipImage == 1 and videofile == False:    	
        rads = rads*-1
    return math.degrees (rads)

def rgb2yuv(rgb):
    m = np.array([
        [0.29900, -0.147108,  0.614777],
        [0.58700, -0.288804, -0.514799],
        [0.11400,  0.435912, -0.099978]
    ])
    yuv = np.dot(rgb, m)
    yuv[:,:,1:] += 0.5
    return yuv

def yuv2rgb(yuv):
    m = np.array([
        [1.000,  1.000, 1.000],
        [0.000, -0.394, 2.032],
        [1.140, -0.581, 0.000],
    ])
    yuv[:, :, 1:] -= 0.5
    rgb = np.dot(yuv, m)
    return rgb

# allow the camera or video file to warm up
time.sleep(0.5)

previousFrame = cv2.Mat

while True:
    # set the frameTime
    frameTime = time.time()
    fpsqueue.append(frameTime)
    
    actualFPS = actualFPS + 1
    videoTimeDiff = fpsqueue[len(fpsqueue)-1] - fpsqueue[0]
    if videoTimeDiff != 0:
        fps = len(fpsqueue) / videoTimeDiff
    else:
        fps = 0

    if args.get("img", False):
        frame = cv2.imread(args["img"])
    else:
        # check for calibration
        ret, frame = vs.read()
        if ps4 == 1 and frame is not None:
            leftframe, rightframe = decode(frame)
            frame = leftframe
        # flip image on y-axis
        if flipImage == 1 and videofile == False:	
            frame = cv2.flip(frame, flipImage)
# FISHEYE View           
        if undistort_video == True and K_test == 1:
            dim3 = dim2 = frame.shape[:2][::-1]
            new_K = cv2.fisheye.estimateNewCameraMatrixForUndistortRectify(scaled_K, D, dim2, np.eye  (3), balance=balance)
            map1, map2 = cv2.fisheye.initUndistortRectifyMap(scaled_K, D, np.eye(3), new_K, dim3, cv2.CV_16SC2)
            frame = cv2.remap(frame, map1, map2, interpolation=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT)
        if undistort_video == True and P_test == 1:
            frame = correct_perspective_image(frame)
# FISHEYE View 
        if flip_video == True:
            frame = cv2.flip(frame, 1)  
        if args["ballcolor"] == "calibrate":
            if record == False:
                if args.get("debug", False):
                    cv2.waitKey(int(args["debug"]))
                if frame is None:
                    calColorObjectCount.append((calibrationcolor[colorcount][0],calObjectCount))
                    colorcount += 1
                    calObjectCount = 0
                    if colorcount == len(calibrationcolor):
                        vs.release()
                        vs = cv2.VideoCapture(webcamindex)
                        videofile = False
                        #vs.set(cv2.CAP_PROP_FPS, 60)
                        ret, frame = vs.read()
                        # flip image on y-axis
                        if flipImage == 1 and videofile == False:    	
                            frame = cv2.flip(frame, flipImage)
                        print("Calibration Finished:"+str(calColorObjectCount))
                        cv2.putText(frame,"Calibration Finished:",(150,100),cv2.FONT_HERSHEY_SIMPLEX,0.5,(0, 0, 255))
                        i = 20
                        texty = 100
                        for calObject in calColorObjectCount:
                            texty = texty+i
                            cv2.putText(frame,str(calObject),(150,texty),cv2.FONT_HERSHEY_SIMPLEX,0.5,(0, 0, 255))
                        texty = texty+i
                        cv2.putText(frame,"Hit any key and choose color with the highest count.",(150,texty),cv2.FONT_HERSHEY_SIMPLEX,0.5,(0, 0, 255))
                        cv2.imshow("Putting View: Press Q to exit / changing Ball Color", frame)
                        cv2.waitKey(0)
                        # Show Results back to Connect App and set directly highest count - maybe also check for false Exit lowest value if 2 colors have equal hits
                        break
                    else:
                        vs.release()                        
                        # grab the calibration video
                        vs = cv2.VideoCapture('Calibration.mp4')
                        videofile = True
                        # grab the current frame
                        ret, frame = vs.read()
                else:
                    hsvVals = calibrationcolor[colorcount][1]
                    if args.get("debug", False):
                        myColorFinder.setTrackbarValues(hsvVals)
                    cv2.putText(frame,"Calibration Mode:"+str(calibrationcolor[colorcount][0]),(200,100),cv2.FONT_HERSHEY_SIMPLEX,0.5,(0, 0, 255))
            else:
                if (frameTime - calibrationtime) > calibrationTimeFrame:
                    record =  False
                    out2.release()
                    vs.release()
                    # grab the calibration video
                    vs = cv2.VideoCapture('Calibration.mp4')
                    videofile = True
                    # grab the current frame
                    ret, frame = vs.read()
                cv2.putText(frame,"Calibration Mode:",(200,100),cv2.FONT_HERSHEY_SIMPLEX,0.5,(0, 0, 255)) 

        # if we are viewing a video and we did not grab a frame,
        # then we have reached the end of the video
        if frame is None:
            print("no frame")
            frame = cv2.imread("error.png")
            cv2.putText(frame,"Error: "+"No Frame",(20, 20),cv2.FONT_HERSHEY_SIMPLEX,0.5,(0, 0, 255))
            cv2.putText(frame,"Message: "+message,(20, 40),cv2.FONT_HERSHEY_SIMPLEX,0.5,(0, 0, 255))
            cv2.imshow("Putting View: Press q to exit / a for adv. settings", frame)
            cv2.waitKey(0)
            break

    origframe = frame.copy()
  
    
    cv2.normalize(frame, frame, 0-darkness, 255-darkness, norm_type=cv2.NORM_MINMAX)
       
    # cropping needed for video files as they are too big
    if args.get("debug", False):   
        # wait for debugging
        cv2.waitKey(int(args["debug"]))
    
    # resize the frame, blur it, and convert it to the HSV
    # color space
    frame = imutils.resize(frame, width=640, height=360)  
    blurred = cv2.GaussianBlur(frame, (11, 11), 0)
    hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)

    # construct a mask for the color "green", then perform
    # a series of dilations and erosions to remove any small
    # blobs left in the mask
    
    # Find the Color Ball
    
    imgColor, mask, newHSV = myColorFinder.update(hsv, hsvVals)    
    
    if hsvVals != newHSV:
        print(newHSV)
        parser.set('putting', 'customhsv', str(newHSV)) #['hmin']+newHSV['smin']+newHSV['vmin']+newHSV['hmax']+newHSV['smax']+newHSV['vmax']))
        parser.write(open(CFG_FILE, "w"))
        hsvVals = newHSV
        print("HSV values changed - Custom Color Set to config.ini")



    mask = mask[y1:y2, sx1:640]

    # Mask now comes from ColorFinder
    #mask = cv2.erode(mask, None, iterations=1)
    #mask = cv2.dilate(mask, None, iterations=5)

    # find contours in the mask and initialize the current
    # (x, y) center of the ball
    cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # testing with cirlces
    # grayframe = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    # circles = cv2.HoughCircles(blurred,cv2.HOUGH_GRADIENT,1,10) 
    # # loop over the (x, y) coordinates and radius of the circles
    # if (circles and len(circles) >= 1):
    #     for (x, y, r) in circles:
    #         cv2.circle(frame, (x, y), r, (0, 255, 0), 4)
    #         cv2.rectangle(frame, (x - 5, y - 5), (x + 5, y + 5), (0, 128, 255), -1)


    cnts = imutils.grab_contours(cnts)
    center = None
    
    # Startpoint Zone

    cv2.line(frame, (startcoord[0][0], startcoord[0][1]), (startcoord[1][0], startcoord[1][1]), (0, 210, 255), 2)  # First horizontal line
    cv2.line(frame, (startcoord[0][0], startcoord[0][1]), (startcoord[2][0], startcoord[2][1]), (0, 210, 255), 2)  # Vertical left line
    cv2.line(frame, (startcoord[2][0], startcoord[2][1]), (startcoord[3][0], startcoord[3][1]), (0, 210, 255), 2)  # Second horizontal line
    cv2.line(frame, (startcoord[1][0], startcoord[1][1]), (startcoord[3][0], startcoord[3][1]), (0, 210, 255), 2)  # Vertical right line

    # Detection Gateway

    cv2.line(frame, (coord[0][0], coord[0][1]), (coord[1][0], coord[1][1]), (0, 0, 255), 2)  # First horizontal line
    cv2.line(frame, (coord[0][0], coord[0][1]), (coord[2][0], coord[2][1]), (0, 0, 255), 2)  # Vertical left line
    cv2.line(frame, (coord[2][0], coord[2][1]), (coord[3][0], coord[3][1]), (0, 0, 255), 2)  # Second horizontal line
    cv2.line(frame, (coord[1][0], coord[1][1]), (coord[3][0], coord[3][1]), (0, 0, 255), 2)  # Vertical right line

    cnts = sorted(cnts, key=cv2.contourArea, reverse=True)
    # only proceed if at least one contour was found
    if len(cnts) > 0:

        x = 0
        y = 0
        radius = 0
        center= (0,0)
        
        for index in range(len(cnts)):
            circle = (0,0,0)
            center= (0,0)
            radius = 0
            # Eliminate countours that are outside the y dimensions of the detection zone
            ((tempcenterx, tempcentery), tempradius) = cv2.minEnclosingCircle(cnts[index])
            tempcenterx = tempcenterx + sx1
            tempcentery = tempcentery + y1
            if (tempcentery >= y1 and tempcentery <= y2):
                rangefactor = 150
                cv2.drawContours(mask, cnts, index, (60, 255, 255), 1)
                cv2.putText(frame,"Radius:"+str(int(tempradius)),(int(tempcenterx)+3, int(tempcentery)),cv2.FONT_HERSHEY_SIMPLEX,0.5,(0, 0, 255))
                # Eliminate countours significantly different than startCircle by comparing radius in range
                if (started == True and startCircle[2]+rangefactor > tempradius and startCircle[2]-10 < tempradius):
                    x = int(tempcenterx)
                    y = int(tempcentery)
                    radius = int(tempradius)
                    center= (x,y)
                else:
                    if not started:
                        x = int(tempcenterx)
                        y = int(tempcentery)
                        radius = int(tempradius)
                        center= (x,y)
                        #print("No Startpoint Set Yet: "+str(center)+" "+str(startCircle[2]+rangefactor)+" > "+str(radius)+" AND "+str(startCircle[2]-rangefactor)+" < "+str(radius))
            else:
                break
            
            
            #print(cnts)
            

            # only proceed if the radius meets a minimum size
            if radius >=5:
                # draw the circle and centroid on the frame,
                # then update the list of tracked points  
                circle = (x,y,radius)
                if circle:
                    # check if the circle is stable to detect if a new start is there
                    if not started or startPos[0]+10 <= center[0] or startPos[0]-10 >= center[0]:
                        if (center[0] >= sx1 and center[0] <= sx2):
                            startCandidates.append(center)
                            if len(startCandidates) > startminimum :
                                startCandidates.pop(0)
                                #filtered = startCandidates.filter(center.x == value.x and center.y == value.y)
                                arr = np.array(startCandidates)
                                # Create an empty list
                                filter_arr = []
                                # go through each element in arr
                                for element in arr:
                                # if the element is completely divisble by 2, set the value to True, otherwise False
                                    if (element[0] == center[0] and center[1] == element[1]):
                                        filter_arr.append(True)
                                    else:
                                        filter_arr.append(False)

                                filtered = arr[filter_arr]

                                #print(filtered)
                                if len(filtered) >= (startminimum/2):
                                    print("New Start Found")
                                    lastShotSpeed = 0
                                    pts.clear()
                                    tims.clear()
                                    filteredcircles = []
                                    filteredcircles.append(circle)
                                    startCircle = circle
                                    startPos = center
                                    startTime = frameTime
                                    #print("Start Position: "+ str(startPos[0]) +":" + str(startPos[1]))
                                    # Calculate the pixel per mm ratio according to z value of circle and standard radius of 2133 mm
                                    if ballradius == 0:
                                        pixelmmratio = circle[2] / golfballradius
                                    else:
                                        pixelmmratio = ballradius / golfballradius
                                    #print("Pixel ratio to mm: " +str(pixelmmratio))    
                                    started = True            
                                    entered = False
                                    left = False
                                    # update the points and tims queues
                                    pts.appendleft(center)
                                    tims.appendleft(frameTime)

                        else:

                            if (x >= coord[0][0] and entered == False and started == True):
                                cv2.line(frame, (coord[0][0], coord[0][1]), (coord[2][0], coord[2][1]), (0, 255, 0),2)  # Changes line color to green
                                tim1 = frameTime
                                print("Ball Entered. Position: "+str(center))
                                startPos = center
                                entered = True
                                # update the points and tims queues
                                pts.appendleft(center)
                                tims.appendleft(frameTime)
                                break
                            else:
                                if ( x > coord[1][0] and entered == True and started == True):
                                    #calculate hla for circle and pts[0]
                                    previousHLA = (GetAngle((startCircle[0],startCircle[1]),pts[0])*-1)
                                    #calculate hla for circle and now
                                    currentHLA = (GetAngle((startCircle[0],startCircle[1]),center)*-1)
                                    #check if HLA is inverted
                                    similarHLA = False
                                    if left == True:
                                        if ((previousHLA <= 0 and currentHLA <=2) or (previousHLA >= 0 and currentHLA >=-2)):
                                            hldDiff = (pow(currentHLA, 2) - pow(previousHLA, 2))
                                            if  hldDiff < 30:
                                                similarHLA = True
                                        else:
                                            similarHLA = False
                                    else:
                                        similarHLA = True
                                    if ( x > (pts[0][0]+50)and similarHLA == True): # and (pow((y - (pts[0][1])), 2)) <= pow((y - (pts[1][1])), 2) 
                                        cv2.line(frame, (coord[1][0], coord[1][1]), (coord[3][0], coord[3][1]), (0, 255, 0),2)  # Changes line color to green
                                        tim2 = frameTime # Final time
                                        print("Ball Left. Position: "+str(center))
                                        left = True
                                        endPos = center
# FISHEYE                                        
                                        # CBS: This is where we do fisheye correction on the two corredinates (startPos, and endPos).
                                        # This will create Two new positions (fstartPos, and fendPos).  Note.   Need to test undistort view alternative to this.
                                        # if K_test == 1 and undistort == 0:
                                        if K_test == 1:
                                              distortedPoints = np.array([[startPos[0], startPos[1]],[endPos[0], endPos[1]]]).astype('float32').reshape(-1,1,2)
                                              # Undistorting the points using OpenCV's undistortPoints() function
                                              undistortedPoints = (cv2.fisheye.undistortPoints(distortedPoints, K, D, P=scaled_K).reshape(-1,2)).astype(int)
                                              print (undistortedPoints)
                                              start_undistortedPoints = tuple(undistortedPoints[0])
                                              end_undistortedPoints = tuple(undistortedPoints[1])
                                              # calculate the distance traveled by the ball in pixel. Once it all looks good, remove the debug code
                                              a = endPos[0] - startPos[0]
                                              b = endPos[1] - startPos[1]
                                              distanceTraveled = math.sqrt( a*a + b*b )
                                              c = end_undistortedPoints[0] - start_undistortedPoints[0]
                                              d = end_undistortedPoints[1] - start_undistortedPoints[1]
                                              new_distanceTraveled = math.sqrt( c*c + d*d )  
                                              print("Old Start Position: "+str(startPos)+" Old End Position: "+str(endPos)+ " Old Distance: "+str(distanceTraveled))
                                              print("New Start Position: "+str(start_undistortedPoints)+" New End Position: "+str(end_undistortedPoints)+" New Distance: "+str(new_distanceTraveled))
                                              startPos = start_undistortedPoints
                                              endPos = end_undistortedPoints
                                        else:
                                              pass
                                        if P_test == 1:
                                            s = correct_perspective_point(startPos)
                                            e = correct_perspective_point(endPos)
                                            print("Old Start Position: "+str(startPos)+" Old End Position: "+str(endPos)) 
                                            print("New Start Position: "+str(s)+" New End Position: "+str(e))   
                                            startPos = s
                                            endPos = e   
# ENDFISHEYE
                                        # calculate the distance traveled by the ball in pixel
                                        a = endPos[0] - startPos[0]
                                        b = endPos[1] - startPos[1]
                                        distanceTraveled = math.sqrt( a*a + b*b )
                                        if not pixelmmratio is None:
                                            # convert the distance traveled to mm using the pixel ratio
                                            distanceTraveledMM = distanceTraveled / pixelmmratio
                                            # take the time diff from ball entered to this frame
                                            timeElapsedSeconds = (tim2 - tim1)
                                            # calculate the speed in MPH
                                            if not timeElapsedSeconds  == 0:
                                                speed = ((distanceTraveledMM / 1000 / 1000) / (timeElapsedSeconds)) * 60 * 60 * 0.621371
                                                if stimp:
                                                    speed *= stimp   # Local Stimp Adjustment
                                                     
                                            # debug out
                                            print("Time Elapsed in Sec: "+str(timeElapsedSeconds))
                                            print("Distance travelled in MM: "+str(distanceTraveledMM))
                                            print("Speed: "+str(speed)+" MPH")
                                            # Calculate local stimp.  ((Vf - Vi) * 0.8200) / ((tf - ti) * 9.8)m/s^2
                                            if lspeed0 == 0:
                                                lspeed0 = distanceTraveledMM / timeElapsedSeconds
                                                ltime0 = timeElapsedSeconds
                                            else:
                                                lspeed1 = distanceTraveledMM / timeElapsedSeconds
                                                ltime1 = timeElapsedSeconds
                                                # We are decelerating so Vf < Vi so just sub Delta V
                                                if lspeed1 < lspped0:
                                                  temp = lspeed1
                                                  lspeed1 = lspeed0
                                                  lspeed0 = temp
                                                  
                                                # Insert a local stimp measurement.   It goes, stimp = (V0^2 - V1^2) / (2 * D * g)
                                                lstimpMM = abs((lspeed1 - lspeed0)) / ((ltime1 - ltime0) * 9806.65) # g=9806.65 mm/s^2.
                                                print("lspeed1="+str(lspeed1)+" lspeed0="+str(lspeed0)+" ltime1="+str(ltime1)+" ltime0="+str(ltime0))
                                                local_stimp = local_stimpMM / 0.8200
                                                print("Local Stimp rating: "+str(local_stimp))
                                                lspeed0 = lspeed1
                                                                                            
                                            # update the points and tims queues
                                            pts.appendleft(center)
                                            tims.appendleft(frameTime)
                                            break
                                    else:
                                        print("False Exit after the Ball")
                                    
    cv2.putText(frame,"Start Ball",(20,20),cv2.FONT_HERSHEY_SIMPLEX,0.5,(0, 0, 255))
    cv2.putText(frame,"x:"+str(startCircle[0]),(20,40),cv2.FONT_HERSHEY_SIMPLEX,0.5,(0, 0, 255))
    cv2.putText(frame,"y:"+str(startCircle[1]),(20,60),cv2.FONT_HERSHEY_SIMPLEX,0.5,(0, 0, 255))

    if ballradius == 0:
        cv2.putText(frame,"radius:"+str(startCircle[2]),(20,80),cv2.FONT_HERSHEY_SIMPLEX,0.5,(0, 0, 255))
    else:
        cv2.putText(frame,"radius:"+str(startCircle[2])+" fixed at "+str(ballradius),(20,80),cv2.FONT_HERSHEY_SIMPLEX,0.5,(0, 0, 255))    

    cv2.putText(frame,"Actual FPS: %.2f" % fps,(200,20),cv2.FONT_HERSHEY_SIMPLEX,0.5,(0, 0, 255))
    if overwriteFPS != 0:
        cv2.putText(frame,"Fixed FPS: %.2f" % overwriteFPS,(400,20),cv2.FONT_HERSHEY_SIMPLEX,0.5,(0, 0, 255))
    else:
        cv2.putText(frame,"Detected FPS: %.2f" % video_fps[0],(400,20),cv2.FONT_HERSHEY_SIMPLEX,0.5,(0, 0, 255))
    # Mark Start Circle
    if started:
        cv2.circle(frame, (startCircle[0],startCircle[1]), startCircle[2],(0, 0, 255), 2)
        cv2.circle(frame, (startCircle[0],startCircle[1]), 5, (0, 0, 255), -1) 

    # Mark Entered Circle
    if entered:
        cv2.circle(frame, (startPos), startCircle[2],(0, 0, 255), 2)
        cv2.circle(frame, (startCircle[0],startCircle[1]), 5, (0, 0, 255), -1)  

    # Mark Exit Circle
    if left:
        cv2.circle(frame, (endPos), startCircle[2],(0, 0, 255), 2)
        cv2.circle(frame, (startCircle[0],startCircle[1]), 5, (0, 0, 255), -1)  




    # loop over the set of tracked points
    for i in range(1, len(pts)):
        
        # if either of the tracked points are None, ignore
        # them
        if pts[i - 1] is None or pts[i] is None:
            continue

        # otherwise, compute the thickness of the line and
        # draw the connecting lines
        thickness = int(np.sqrt(args["buffer"] / float(i + 1)) * 1.5)
        #cv2.line(frame, pts[i - 1], pts[i], (0, 0, 150), thickness)
        # print("Point:"+str(pts[i])+"; Timestamp:"+str(tims[i]))

    timeSinceEntered = (frameTime - tim1)

    if left == True:

        # Send Shot Data
        if (tim2 and timeSinceEntered > 0.5 and distanceTraveledMM and timeElapsedSeconds and speed >= 0.5 and speed <= 25):
            print("----- Shot Complete --------")
            print("Time Elapsed in Sec: "+str(timeElapsedSeconds))
            print("Distance travelled in MM: "+str(distanceTraveledMM))
            print("Speed: "+str(speed)+" MPH")

            #     ballSpeed: ballData.BallSpeed,
            #     totalSpin: ballData.TotalSpin,
            totalSpin = 0
            #     hla: ballData.LaunchDirection,
            launchDirection = (GetAngle((startCircle[0],startCircle[1]),endPos)*-1)
            print("HLA: Line"+str((startCircle[0],startCircle[1]))+" Angle "+str(launchDirection))
            #Decimal(launchDirection);
            if (launchDirection > -40 and launchDirection < 40):

                lastShotStart = (startCircle[0],startCircle[1])
                lastShotEnd = endPos
                lastShotSpeed = speed
                lastShotHLA = launchDirection
                    
                # Data that we will send in post request.
                data = {"ballData":{"BallSpeed":"%.2f" % speed,"TotalSpin":totalSpin,"LaunchDirection":"%.2f" % launchDirection}}

                # The POST request to our node server
                if args["ballcolor"] == "calibrate":
                    print("calibration mode - shot data not send")
                else:
                    try:
                        res = requests.post('http://127.0.0.1:8888/putting', json=data)
                        res.raise_for_status()
                        # Convert response data to json
                        returned_data = res.json()

                        print(returned_data)
                        result = returned_data['result']
                        print("Response from Node.js:", result)

                    except requests.exceptions.HTTPError as e:  # This is the correct syntax
                        print(e)
                    except requests.exceptions.RequestException as e:  # This is the correct syntax
                        print(e)
            else:
                print("Misread on HLA - Shot not send!!!")    
            if len(pts) > calObjectCount:
                calObjectCount = len(pts)
            print("----- Data reset --------")
            started = False
            entered = False
            left = False
            speed = 0
            timeSinceEntered = 0
            tim1 = 0
            tim2 = 0
            distanceTraveledMM = 0
            timeElapsedSeconds = 0
            lspeed0 = 0
            startCircle = (0, 0, 0)
            endCircle = (0, 0, 0)
            startPos = (0,0)
            endPos = (0,0)
            startTime = time.time()
            pixelmmratio = 0
            pts.clear()
            tims.clear()

            # Further clearing - startPos, endPos
    else:
        # Send Shot Data
        if (tim1 and timeSinceEntered > 0.5):
            print("----- Data reset --------")
            started = False
            entered = False
            left = False
            speed = 0
            timeSinceEntered = 0
            tim1 = 0
            tim2 = 0
            distanceTraveledMM = 0
            timeElapsedSeconds = 0
            lspeed0 = 0
            startCircle = (0, 0, 0)
            endCircle = (0, 0, 0)
            startPos = (0,0)
            endPos = (0,0)
            startTime = time.time()
            pixelmmratio = 0
            pts.clear()
            tims.clear()
            
    #cv2.putText(frame,"entered:"+str(entered),(20,180),cv2.FONT_HERSHEY_SIMPLEX,0.5,(0, 0, 255))
    #cv2.putText(frame,"FPS:"+str(fps),(20,200),cv2.FONT_HERSHEY_SIMPLEX,0.5,(0, 0, 255))

    if not lastShotSpeed == 0:
        cv2.line(frame,(lastShotStart),(lastShotEnd),(0, 255, 255),4,cv2.LINE_AA)      
        cv2.putText(frame,"Last Shot",(400,40),cv2.FONT_HERSHEY_SIMPLEX,0.5,(0, 0, 255),1)
        cv2.putText(frame,"Ball Speed: %.2f" % lastShotSpeed+" MPH",(400,60),cv2.FONT_HERSHEY_SIMPLEX,0.5,(0, 0, 255),1)
        cv2.putText(frame,"HLA:  %.2f" % lastShotHLA+" Degrees",(400,80),cv2.FONT_HERSHEY_SIMPLEX,0.5,(0, 0, 255),1)
    
    if started:
        cv2.line(frame,(sx2,startCircle[1]),(sx2+400,startCircle[1]),(255, 255, 255),4,cv2.LINE_AA)
    else:
        cv2.line(frame,(sx2,int(y1+((y2-y1)/2))),(sx2+400,int(y1+((y2-y1)/2))),(255, 255, 255),4,cv2.LINE_AA) 
    
    #if args.get("video", False):
    #    out1.write(frame)

    if out2:
        try:
            out2.write(origframe)
        except Exception as e:
            print(e)
    
    # show main putting window

    outputframe = resizeWithAspectRatio(frame, width=int(args["resize"]))
    cv2.imshow("Putting View: Press q to exit / a=adv f=flip s=stimp u=undistort v=video w=write_video", outputframe)
    
    
    #cv2.moveWindow("Putting View: Press q to exit / a for adv. settings", 20,20)

    # cv2.namedWindow("Putting View: Press q to exit / a for adv. settings",cv2.WINDOW_KEEPRATIO)
    # Resize the Window
    # cv2.resizeWindow("Putting View: Press q to exit / a for adv. settings", 340, 240)
    
    if args.get("debug", False):
        cv2.imshow("MaskFrame", mask)
        cv2.imshow("Original", origframe)
    
    key = cv2.waitKey(1) & 0xFF
    # if the 'q' key is pressed, stop the loop
    if key == ord("q"):
        break
    if key == ord("a"):
        if not a_key_pressed:
            cv2.namedWindow("Advanced Settings")
            if mjpegenabled != 0:
                vs.set(cv2.CAP_PROP_SETTINGS, 37)  
            cv2.resizeWindow("Advanced Settings", 1000, 400)
            cv2.createTrackbar("X Start", "Advanced Settings", int(sx1), 640, setXStart)
            cv2.createTrackbar("X End", "Advanced Settings", int(sx2), 640, setXEnd)
            cv2.createTrackbar("Y Start", "Advanced Settings", int(y1), 460, setYStart)
            cv2.createTrackbar("Y End", "Advanced Settings", int(y2), 460, setYEnd)
            cv2.createTrackbar("Radius", "Advanced Settings", int(ballradius), 50, setBallRadius)
            cv2.createTrackbar("Flip Image", "Advanced Settings", int(flipImage), 1, setFlip)
            cv2.createTrackbar("MJPEG", "Advanced Settings", int(mjpegenabled), 1, setMjpeg)
            cv2.createTrackbar("FPS", "Advanced Settings", int(overwriteFPS), 240, setOverwriteFPS)
            cv2.createTrackbar("Darkness", "Advanced Settings", int(darkness), 255, setDarkness)
            a_key_pressed = True
        else:
            cv2.destroyWindow("Advanced Settings")
            a_key_pressed = False
            
    if key == ord("d"):
        args["debug"] = 1
        myColorFinder = ColorFinder(True)
        myColorFinder.setTrackbarValues(hsvVals)

    #CB: Added a way to store video properties
    if key == ord("v"):
        vs.set(cv2.CAP_PROP_SETTINGS, 1)
    if key == ord("w"):
        print("Writing config file with video options")
        brightness = vs.get(cv2.CAP_PROP_BRIGHTNESS)
        contrast = vs.get(cv2.CAP_PROP_CONTRAST)
        hue = vs.get(cv2.CAP_PROP_HUE)
        saturation = vs.get(cv2.CAP_PROP_SATURATION)
        exposure = vs.get(cv2.CAP_PROP_EXPOSURE)  # -7 means 2^-7 = 1/(2^7) = 1/128 sec.  A value of -1 = 2^(-1) = 1/(2^1) = 1/2 sec exposure time or 2FPS. 
        # Auto_exposure has a bug in that get and set require different value.  The get returns a -1,0 = automatic, 0.0 = manual.  
        auto_exposure = vs.get(cv2.CAP_PROP_AUTO_EXPOSURE) # CAP_PROP_AUTO_EXPOSURE set is 0.25 this means manual, 0.75 sets it to automatic. *workaround bug*
        gamma = vs.get(cv2.CAP_PROP_GAMMA)
        gain = vs.get(cv2.CAP_PROP_GAIN)

        if not parser.has_section('camera_properties'):
            parser.add_section('camera_properties')
        parser.set('camera_properties', 'brightness', str(brightness))
        parser.set('camera_properties', 'contrast', str(contrast))
        parser.set('camera_properties', 'hue', str(hue))
        parser.set('camera_properties', 'saturation', str(saturation))
        parser.set('camera_properties', 'exposure', str(exposure))
        parser.set('camera_properties', 'auto_exposure', str(auto_exposure))
        parser.set('camera_properties', 'gamma', str(gamma))
        parser.set('camera_properties', 'gain', str(gain))
        parser.set('camera_properties', 'webcamindex', str(webcamindex))
        with open(CFG_FILE, 'w') as config_file:
           parser.write(config_file)
    if key == ord("u"):
        if not  undistort_video:
          undistort_video = True;
        else:
          undistort_video = False;
    if key == ord("f"):
        if not  flip_video:
          flip_video = True;
        else:
          flip_video = False;
    # We really need a way to change webcams so we can quickly swithch them if we select the wrong cam.
    # The question is do we need to change the window size as well, or can we simply switch cameras.
    # For now, lets leave the window alone and let the opencv handle it. Max 4 webcams / USB controller.
    # DSHOW assumes a windows machine BTW.  Also note: the distortion paramters will not change.
    if key == ord("c"):
        cam_webcamindex = cam_webcamindex + 1
        if cam_webcamindex > 3:
          cam_webcamindex = 0
        print("New Webcam: "+str(cam_webcamindex))
        vs.release()
        stop_loop = 0 
        while True: 
          webcamindex = cam_webcamindex           
          vs = cv2.VideoCapture(webcamindex + cv2.CAP_DSHOW)
          if stop_loop == 0 and vs is None or not vs.isOpened():
              print("Webcam "+str(webcamindex)+" does not exist or can't be opened.")
              cam_webcamindex = cam_webcamindex + 1
              if cam_webcamindex > 3:
                cam_webcamindex = 0
                stop_loop = 1
              continue
          else:
            break
            
        if stop_loop == 1:
          pass 
        else:   
          video_fps = vs.get(cv2.CAP_PROP_FPS)
          height = vs.get(cv2.CAP_PROP_FRAME_HEIGHT)
          width = vs.get(cv2.CAP_PROP_FRAME_WIDTH)
          brightness = vs.get(cv2.CAP_PROP_BRIGHTNESS)
          contrast = vs.get(cv2.CAP_PROP_CONTRAST)
          hue = vs.get(cv2.CAP_PROP_HUE)
          saturation = vs.get(cv2.CAP_PROP_SATURATION)
          exposure = vs.get(cv2.CAP_PROP_EXPOSURE)  # -7 means 2^-7 = 1/(2^7) = 1/128 sec.  A value of -1 = 2^(-1) = 1/(2^1) = 1/2 sec exposure time or 2FPS. 
          # Auto_exposure has a bug in that get and set require different value.  The get returns a -1,0 = automatic, 0.0 = manual.  
          auto_exposure = vs.get(cv2.CAP_PROP_AUTO_EXPOSURE) # CAP_PROP_AUTO_EXPOSURE set is 0.25 this means manual, 0.75 sets it to automatic. *workaround bug*
          gamma = vs.get(cv2.CAP_PROP_GAMMA)
          gain = vs.get(cv2.CAP_PROP_GAIN)

    if key == ord("s"):
        if not s_key_pressed:
            cv2.namedWindow("Local_Stimp")
            cv2.setWindowTitle("Local_Stimp","Local Stimp Adjustment = (0 to 200) / 100.0 : Default=100")
            istimp = int(stimp * 100.0)
            cv2.resizeWindow("Local_Stimp",640, 50)
            cv2.createTrackbar("L_Stimp: ", "Local_Stimp", istimp, 200, setStimp)
            stimp=(float(istimp)/100.0)
            s_key_pressed = True
        else:
            cv2.destroyWindow("Local_Stimp")
            s_key_pressed = False
    else:
        pass
          
    if actualFPS > 1:
        grayPreviousFrame = cv2.cvtColor(previousFrame, cv2.COLOR_BGR2GRAY)
        grayOrigframe = cv2.cvtColor(origframe, cv2.COLOR_BGR2GRAY)
        changedFrame = cv2.compare(grayPreviousFrame, grayOrigframe,cv2.CMP_NE)
        nz = cv2.countNonZero(changedFrame)
        #print(nz)
        if nz == 0:
            actualFPS = actualFPS - 1
            fpsqueue.pop()
    previousFrame = origframe.copy()


# close all windows
vs.release()
cv2.destroyAllWindows()
