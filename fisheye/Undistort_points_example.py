import cv2
import numpy as np

# Read in the image
img = cv2.imread('path/to/image.jpg')

# Define the camera matrix, distortion coefficients, and the fisheye calibration flag
K = np.array([[fx, 0, cx], [0, fy, cy], [0, 0, 1]]) # camera matrix
D = np.array([k1, k2, k3, k4]) # distortion coefficients
flags = cv2.fisheye.CALIB_RECOMPUTE_EXTRINSIC + cv2.fisheye.CALIB_CHECK_COND + cv2.fisheye.CALIB_FIX_SKEW # fisheye calibration flag

# Calibrate the fisheye lens
img_shape = img.shape[:2]
new_K = cv2.fisheye.estimateNewCameraMatrixForUndistortRectify(K, D, img_shape, np.eye(3), flags=flags)
map1, map2 = cv2.fisheye.initUndistortRectifyMap(K, D, np.eye(3), new_K, img_shape[::-1], cv2.CV_16SC2)

# Define the coordinates of the two points in the original image
pt1 = (x1, y1)
pt2 = (x2, y2)

# Print the locations of the points in the original image
print("Point 1 in original image:", pt1)
print("Point 2 in original image:", pt2)

# Use the map coordinates to find the corresponding points in the undistorted image
undistorted_pt1 = tuple(map(int, map1[y1][x1]))
undistorted_pt2 = tuple(map(int, map1[y2][x2]))

# Print the locations of the corresponding points in the undistorted image
print("Point 1 in undistorted image:", undistorted_pt1)
print("Point 2 in undistorted image:", undistorted_pt2)

# Display the original and undistorted images
cv2.imshow('Original Image', img)
undistorted_img = cv2.remap(img, map1, map2, interpolation=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT)
cv2.imshow('Undistorted Image', undistorted_img)
cv2.waitKey(0)
cv2.destroyAllWindows()
