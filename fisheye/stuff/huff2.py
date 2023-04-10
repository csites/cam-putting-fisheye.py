import cv2
import numpy as np

# Load an image
img = cv2.imread("./input.jpg")
cv2.imshow('Corrected Image', img)
# Convert the image to grayscale
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

# Apply Canny edge detection to find edges
edges = cv2.Canny(gray, 50, 150, apertureSize=3)

# Run the Hough Line Transform to find lines in the edges image
lines = cv2.HoughLines(edges, rho=1, theta=np.pi/180, threshold=100)

# Compute the homography matrix
if lines is not None:
    points = []
    for line in lines:
        rho, theta = line[0]
        a = np.cos(theta)
        b = np.sin(theta)
        x0 = a * rho
        y0 = b * rho
        x1 = int(x0 + 1000 * (-b))
        y1 = int(y0 + 1000 * (a))
        x2 = int(x0 - 1000 * (-b))
        y2 = int(y0 - 1000 * (a))
        points.append([x1, y1])
        points.append([x2, y2])

    points = np.array(points)

    # Define the corresponding points in the corrected image
    corrected_points = np.array([[0, 0], [img.shape[1], 0], [img.shape[1], img.shape[0]], [0, img.shape[0]]])

    # Compute the homography matrix
    H, _ = cv2.findHomography(points, corrected_points)

    # Apply the homography to the original image
    corrected_img = cv2.warpPerspective(img, H, (img.shape[1], img.shape[0]))

    # Display the corrected image
    cv2.imshow('Corrected Image', corrected_img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
