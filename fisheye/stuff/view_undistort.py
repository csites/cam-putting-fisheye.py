# Alternative to view fisheye image.
img = cv2.imread(img_path)
img_dim = img.shape[:2][::-1]  

DIM = # dimension of the images used for calibration

scaled_K = K * img_dim[0] / DIM[0]  
scaled_K[2][2] = 1.0  
new_K = cv2.fisheye.estimateNewCameraMatrixForUndistortRectify(scaled_K, D,
    img_dim, np.eye(3), balance=balance)
map1, map2 = cv2.fisheye.initUndistortRectifyMap(scaled_K, D, np.eye(3),
    new_K, img_dim, cv2.CV_16SC2)
undist_image = cv2.remap(img, map1, map2, interpolation=cv2.INTER_LINEAR,
    borderMode=cv2.BORDER_CONSTANT)
    