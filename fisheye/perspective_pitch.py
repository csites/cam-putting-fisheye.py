#
# This pivots an image around the the center horizontal line (of the putting area to make 
# adjustments for perspective distortion.   This will refine the HLA and ball speed for any 
# shot that is not on the putting line center.
#

import cv2
import numpy as np
import glob

def correct_perspective(image, pitch):
    height, width = image.shape[:2]
    center_line = int(height / 2)

    # Calculate the pitch in radians
    pitch_rad = np.radians(pitch)

    # Define the source and destination points for perspective transformation
    src_points = np.float32([[0, center_line], [width, center_line], [0, height], [width, height]])
    dst_points = np.float32([[0, center_line], [width, center_line], [width / 2 - np.tan(pitch_rad) * center_line, height],
                            [width / 2 + np.tan(pitch_rad) * center_line, height]])

    # Compute the perspective transformation matrix
    perspective_matrix = cv2.getPerspectiveTransform(src_points, dst_points)

    # Apply the perspective correction
    corrected_image = cv2.warpPerspective(image, perspective_matrix, (width, height))

    return corrected_image

def main():
    filename = 'perspective/image_2.jpg'
    input_image = cv2.imread(filename)
    cv2.namedWindow('Input', cv2.WINDOW_NORMAL)
    cv2.imshow('Input', input_image)
    
    cv2.namedWindow('Output', cv2.WINDOW_NORMAL)
   
    pitch_angle = 0
    cv2.createTrackbar('Pitch', 'Output', pitch_angle, 90, lambda x: None)

    while True:
        cv2.imshow('Output', correct_perspective(input_image, pitch_angle))

        key = cv2.waitKey(1)
        if key == ord('q'):
            break

        pitch_angle = cv2.getTrackbarPos('Pitch', 'Output')

    cv2.destroyAllWindows()

if __name__ == '__main__':
    main()
