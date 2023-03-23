import cv2
import winsound
import time

print("This program is used to capture a number of images of the checkerboard pattern you printed.")
num_images = input("How many images would you like to take? (Enter a number between 1-25): ")

try:
    num_images = int(num_images)
    if num_images < 1 or num_images > 25:
        raise ValueError("Number of images must be between 1-25")
except ValueError:
    print("Invalid input. Please enter a number between 1-25.")
    exit()
    
frequency = 2500  # Set Frequency To 2500 Hertz
duration = 1000  # Set Duration To 1000 ms == 1 second
time.sleep(5)
winsound.Beep(frequency, duration)

camera = cv2.VideoCapture(0)
for i in range(10):
    return_value, image = camera.read()
    cv2.imwrite('opencv'+str(i)+'.jpg', image)
    time.sleep(5)
    winsound.Beep(frequency, duration)
     
del(camera)

