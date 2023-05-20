import cv2
import numpy as np

# Read the image
image = cv2.imread("perspective/image_1.jpg")

# Convert the image to grayscale
grayscale_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

# Apply Canny edge detection to the image
canny_edges = cv2.Canny(grayscale_image, 50, 150)
cv2.imshow("Canny_Edges", canny_edges)
cv2.waitKey(1)

# Use the Harris corner detection method to find the corners in the image
corners = cv2.cornerHarris(canny_edges, 2, 3, 0.04)

# Select the top 4 corners
top_4_corners = np.argsort(corners)[-4:]

# Draw circles around the corners
for corner in top_4_corners:
    cv2.circle(image, corners[corner], 5, (0, 0, 255), -1)

# Report the coordinates of the corners
corner_coordinates = corners[top_4_corners]

# Display the image
cv2.imshow("Image", image)
cv2.waitKey(0)
cv2.destroyAllWindows()

print(corner_coordinates)