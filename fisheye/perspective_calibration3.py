import numpy as np
import cv2

# Load the input image
img = cv2.imread('Calibrations/image_2.jpg')

# Create a window to display the image.
cv2.namedWindow('Image')

# Bind a mouse callback function to the window.
def on_mouse_move(event, x, y, flags, param):
    global img
    if event == cv2.EVENT_MOUSEMOVE:
        row = y // img.shape[0]
        column = x // img.shape[1]
        # Draw a crosshair at the row and column indices.
        cv2.line(img, (row, column), (row, column), (0, 0, 255), 2)
        cv2.line(img, (row, column), (row + 1, column), (0, 0, 255), 2)
        cv2.line(img, (row, column), (row, column + 1), (0, 0, 255), 2)
        cv2.line(img, (row + 1, column), (row + 1, column + 1), (0, 0, 255), 2)
        
        
# Set the mouse callback function.
cv2.setMouseCallback('Image', on_mouse_move)

# Display the image.
while True:
    cv2.imshow('Image', img)
    k = cv2.waitKey(20) & 0xFF
    if k == 27:
        break

# Close all windows.
cv2.destroyAllWindows()

# Define the dimensions of the chessboard
chessboard_size = (7, 7)  # 7 corners per edge

# Detect the corners of the chessboard in the image
ret, corners = cv2.findChessboardCorners(img, chessboard_size, None)
# Draw the detected corners on the image
cv2.drawChessboardCorners(img, chessboard_size, corners, ret)
cv2.imshow('Input',img)
cv2.waitKey(0)

if ret:

    # Define the coordinates of the four corners of the chessboard in the input image
    
    # Define the coordinates of the four corners of the output image
    h, w = img.shape[:2]   # Output image size in inches
    corners = corners.astype(int)
    minh = corners[:,:,0].min()
    maxh = corners[:,:,0].max()
    minw = corners[:,:,1].min()
    maxw = corners[:,:,1].max()

    # This maps the perspective for the checkerboard to the full screen of the image. That may mess with scale.    
    # And damn, it's hard to get these dumb arrays in the correct format. 
    fc=np.array([ [tuple(corners[0,0])],[tuple(corners[6,0])], [tuple(corners[42,0])], [tuple(corners[48,0])] ],np.float32)
    dc=np.array([ [0,0], [w,0], [0,h], [w,h]],np.float32)

    # Compute the transformation matrix
    # H = cv2.getPerspectiveTransform(fc, dc)
    H, _ret = cv2.findHomography(fc, dc)
    print(H)
    
    # Apply the transformation matrix to the input image
    output_img = cv2.warpPerspective(img, H, (w, h))
    cv2.imshow('Output',output_img)
    cv2.waitKey(0)
    # Save the output image
#    cv2.imwrite('output.jpg', db/output_img.jpg)
else:
    print("Unable to detect chessboard corners in image.")
