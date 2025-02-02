import cv2
import numpy as np

# Define the checkerboard dimensions and square size
checkerboard_size = (7,7)
square_size = 2 # in inches

# Prepare object points, like (0,0,0), (1,0,0), (2,0,0) ....,(8,5,0)
object_points = np.zeros((np.prod(checkerboard_size), 3), dtype=np.float32)
object_points[:, :2] = np.mgrid[0:checkerboard_size[0], 0:checkerboard_size[1]].T.reshape(-1, 2)
object_points *= square_size

# Create arrays to store object points and image points from all images
object_points_list = [] # 3D points in real world space
image_points_list = [] # 2D points in image plane.

# Load the image
image = cv2.imread('checkerboard.jpg')

# Find the corners of the checkerboard in the image
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
ret, corners = cv2.findChessboardCorners(gray, checkerboard_size, None)

# If the corners are found, add object points and image points to the list
if ret:
    object_points_list.append(object_points)
    image_points_list.append(corners)

# Calibrate the camera using the image points and object points
ret, camera_matrix, distortion_coeffs, rvecs, tvecs = cv2.calibrateCamera(object_points_list, image_points_list, gray.shape[::-1], None, None)

# Transform the image points into real-world coordinates
undistorted_image = cv2.undistort(image, camera_matrix, distortion_coeffs)
new_camera_matrix, roi = cv2.getOptimalNewCameraMatrix(camera_matrix, distortion_coeffs, gray.shape[::-1], 1, gray.shape[::-1])
new_image_points = cv2.undistortPoints(corners, camera_matrix, distortion_coeffs, P=new_camera_matrix)

# Select two points in the image and measure their distance in real-world units
point1 = new_image_points[0, 0]
point2 = new_image_points[2, 0]
distance_pixels = np.linalg.norm(point2 - point1)
distance_inches = distance_pixels * square_size / np.linalg.norm(object_points[2] - object_points[0])

print("Distance in pixels:", distance_pixels)
print("Distance in inches:", distance_inches)

# Display the original and undistorted images with the measured distance
cv2.line(undistorted_image, tuple(point1), tuple(point2), (0, 0, 255), 2)
cv2.putText(undistorted_image, f"{distance_inches:.2f} inches", tuple(((point1 + point2) / 2).astype(int)), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
cv2.imshow("Undistorted", undistorted_image)
cv2.waitKey(0
