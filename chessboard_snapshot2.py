import cv2
import time
import winsound
import os

print("Before running this program, you should goto:")
print(" https://markhedleyjones.com/projects/calibration-checkerboard-collection")
print("and create/download and print a custom chessboard pattern for the type")
print("paper your using; default is A4, Custom Standard Letter is 215mm x 279mm.")
print("30mm squares works well")
print("")
print("This program is used to capture a number of images of the checkerboard pattern you printed.")
print("It will beep and pause for 5 seconds before each snapshot.")
print("")
camera_num = input("Enter camera number (0 to 4): ")

try:
    camera_num = int(camera_num)
    if camera_num < 0 or camera_num > 4:
        raise ValueError("Camera number must be between 0-4")
except ValueError:
    print("Invalid input. Please enter a number between 0-4.")
    exit()
print("Move your chessboard to different locations until you have all of the camera covered")    
num_images = input("How many images would you like to take? (Enter a number between 1-125): ")

try:
    num_images = int(num_images)
    if num_images < 1 or num_images > 125:
        raise ValueError("Number of images must be between 1-125")
except ValueError:
    print("Invalid input. Please enter a number between 1-25.")
    exit()


    
# Set up OpenCV camera capture
cap = cv2.VideoCapture(camera_num)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
#cap.set(cv2.CAP_PROP_FPS, 30)
#cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))

calibration_dir = "Calibrations"
# calibration_dir = "db"

if not os.path.exists(calibration_dir):
    os.makedirs(calibration_dir)

for i in range(num_images):
    winsound.Beep(2500, 1000)
    ret, frame = cap.read()
    if not ret:
        print("Error capturing image. Exiting...")
        exit()
#    cv2.imshow(f"image_{i}", frame)
    filename = os.path.join(calibration_dir, f"image_{i}.jpg")
    cv2.imwrite(filename, frame)
    image=cv2.imread(filename)
    cv2.imshow(f"image_{i}", image)
    cv2.waitKey(1)

    print("Move Checkerboard to new position and location")
    time.sleep(5)
    cv2.destroyAllWindows()

cap.release()

