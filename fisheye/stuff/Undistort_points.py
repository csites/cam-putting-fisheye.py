import cv2
import numpy as np
import matplotlib.pyplot as plt

K = np.asarray([[556.3834638575809,0,955.3259939726225],[0,556.2366649196925,547.3011305411478],[0,0,1]])
D = np.asarray([[-0.05165940570900624],[0.0031093602070252167],[-0.0034036648250202746],[0.0003390345044343793]])
print("K:\n", K)
print("D:\n", D.ravel())

# read image and get the original image on the left
image_path = "sample.jpg"
image = cv2.imread(image_path)
image = image[:, :image.shape[1]//2, :]
image_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

fig = plt.figure()
plt.imshow(image_gray, "gray")

H_in, W_in = image_gray.shape
print("Grayscale Image Dimension:\n", (W_in, H_in))

scale_factor = 1.0 
balance = 1.0

img_dim_out =(int(W_in*scale_factor), int(H_in*scale_factor))
if scale_factor != 1.0:
    K_out = K*scale_factor
    K_out[2,2] = 1.0

K_new = cv2.fisheye.estimateNewCameraMatrixForUndistortRectify(K_out, D, img_dim_out, np.eye(3), balance=balance)
print("Newly estimated K:\n", K_new)

map1, map2 = cv2.fisheye.initUndistortRectifyMap(K, D, np.eye(3), K_new, img_dim_out, cv2.CV_32FC1)
print("Rectify Map1 Dimension:\n", map1.shape)
print("Rectify Map2 Dimension:\n", map2.shape)

undistorted_image_gray = cv2.remap(image_gray, map1, map2, interpolation=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT)
fig = plt.figure()
plt.imshow(undistorted_image_gray, "gray")
  
ret, corners = cv2.findChessboardCorners(image_gray, (6,8),cv2.CALIB_CB_ADAPTIVE_THRESH+cv2.CALIB_CB_FAST_CHECK+cv2.CALIB_CB_NORMALIZE_IMAGE)
corners_subpix = cv2.cornerSubPix(image_gray, corners, (3,3), (-1,-1), (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.1))

undistorted_corners = cv2.fisheye.undistortPoints(corners_subpix, K, D)
undistorted_corners = undistorted_corners.reshape(-1,2)


fx = K_new[0,0]
fy = K_new[1,1]
cx = K_new[0,2]
cy = K_new[1,2]
undistorted_corners_pixel = np.zeros_like(undistorted_corners)

for i, (x, y) in enumerate(undistorted_corners):
    px = x*fx + cx
    py = y*fy + cy
    undistorted_corners_pixel[i,0] = px
    undistorted_corners_pixel[i,1] = py
    
undistorted_image_show = cv2.cvtColor(undistorted_image_gray, cv2.COLOR_GRAY2BGR)
for corner in undistorted_corners_pixel:
    image_corners = cv2.circle(np.zeros_like(undistorted_image_show), (int(corner[0]),int(corner[1])), 15, [0, 255, 0], -1)
    undistorted_image_show = cv2.add(undistorted_image_show, image_corners)

fig = plt.figure()
plt.imshow(undistorted_image_show, "gray")