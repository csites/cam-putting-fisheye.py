import numpy as np
import cv2
import numpy as np
import cv2

# Define the size of the chessboard
chessboard_size = (8, 6)

# Define the length of each square on the chessboard (in pixels)
square_length = 50

# Define the coordinates of the chessboard corners in 3D
objpoints = np.zeros((chessboard_size[0] * chessboard_size[1], 3), np.float32)
objpoints[:, :2] = np.indices(chessboard_size).T.reshape(-1, 2) * square_length
objpoints = np.array([objpoints])

# Define the camera matrix and distortion coefficients for the perspective view
K = np.array([[500, 0, 320], [0, 500, 240], [0, 0, 1]], dtype=np.float32) # camera matrix
dist_coeffs = np.array([0, 0, 0, 0], dtype=np.float32) # distortion coefficients

# Define the rotation and translation vectors to apply the perspective view
theta = np.pi/4 # angle of the camera relative to the chessboard (in radians)
rot_vec = np.array([theta, 0, 0], dtype=np.float32) # rotation vector
t_vec = np.array([0, 0, -1000], dtype=np.float32) # translation vector

# Apply the perspective transformation to the chessboard corners
imgpoints, _ = cv2.projectPoints(objpoints, rot_vec, t_vec, K, dist_coeffs)

# Draw the perspective view of the chessboard
img = np.zeros((480, 640), np.uint8)
x_offset = int((640 - imgpoints[0][:, 0].max()) / 2)
y_offset = int((480 - imgpoints[0][:, 1].max()) / 2)
imgpoints[0][:, 0] += x_offset
imgpoints[0][:, 1] += y_offset
cv2.drawChessboardCorners(img, chessboard_size, imgpoints[0], True)

# Resize the image to 640x480
img = cv2.resize(img, (640, 480))

# Save the image as a JPG

# Save the image as a JPG file
cv2.imwrite('perspective_chessboard.jpg', img)
