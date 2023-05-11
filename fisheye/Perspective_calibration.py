import numpy as np
import cv2

import cv2
import numpy as np

# Load the input image
img = cv2.imread('Calibrations/image_2.jpg')

cv2.imshow('Input',img)
cv2.waitKey(0)
# Define the dimensions of the chessboard
chessboard_size = (7, 7)  # 7 corners per edge

# Detect the corners of the chessboard in the image
ret, corners = cv2.findChessboardCorners(img, chessboard_size, None)

if ret:
    # Draw the detected corners on the image
    cv2.drawChessboardCorners(img, chessboard_size, corners, ret)

    # Define the coordinates of the four corners of the chessboard in the input image
    chessboard_corners = np.array([corners[0], corners[6], corners[42], corners[48]], dtype=np.float32)

    # Define the coordinates of the four corners of the output image
    output_width, output_height = 14, 14  # Output image size in inches
    output_corners = np.array([[0, 0], [output_width, 0], [output_width, output_height], [0, output_height]], dtype=np.float32)

    # Compute the transformation matrix
    M = cv2.getPerspectiveTransform(chessboard_corners, output_corners)

    # Apply the transformation matrix to the input image
    output_img = cv2.warpPerspective(img, M, (int(output_width*300), int(output_height*300)))
    cv2.imshow('Output',output_img)
    cv2.waitKey(0)
    # Save the output image
    cv2.imwrite('output.jpg', db/output_img.jpg)
else:
    print("Unable to detect chessboard corners in image.")
