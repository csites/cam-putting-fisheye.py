import cv2
import numpy as np

# Load the image
img = cv2.imread('Calibrations/image_2.jpg')

# Define the checkerboard dimensions
checkerboard_size = (7, 7)

# Find the corners of the checkerboard in the image
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
ret, corners = cv2.findChessboardCorners(gray, checkerboard_size, None)
print("corners="+str(corners))

# Draw the corners on the image for visualization
cv2.drawChessboardCorners(img, checkerboard_size, corners, ret)
cv2.imshow("Original", img)

# Compute the homography matrix
if ret: 
    print("Corners_shape: "+str(corners.shape))
    print("Corners: "+str(corners))
    ncorners=np.array([corners[0,0,:],corners[6,0,:], corners[48-6:,0,:], corners[49-1,0,:]], dtype=np.float32)
    print("ncorners: "+str(ncorners))
    dcorners=np.array( [[ corner[48-6,0,0], corner[0,0,1] ] , [ corner[48,0,1],corner[0,0,1] ] , corners[48-6,0,:], corners[49-1,0,:]], dtype=np.float32)
    print("dcorners: "+str(dcorners))  
    h, _ = cv2.findHomography(corners, dst_corners)
    print("Homography: "+str(h))
    
    # Apply the homography matrix to the image to correct the perspective
    corrected_img = cv2.warpPerspective(img, h, (img.shape[1], img.shape[0]))

    # Display the original and corrected images
    cv2.imshow("Original", img)
    cv2.imshow("Corrected", corrected_img)
    cv2.waitKey(0)
import cv2
import numpy as np

# Compute the homography matrix
if ret:
    corners = np.float32(corners)
    dst_corners = np.array([[0, 0], [8, 0], [8, 5], [0, 5]], dtype=np.float32) * 2 # In inches
    h, _ = cv2.findHomography(corners, dst_corners)

    # Apply the homography matrix to the image to correct the perspective
    corrected_img = cv2.warpPerspective(img, h, (img.shape[1], img.shape[0]))

    # Display the original and corrected images
    cv2.imshow("Original", img)
    cv2.imshow("Corrected", corrected_img)
    cv2.waitKey(0)
