def undistort_list_of_points(point_list, in_K, in_d, in_K_new):
    K = np.asarray(in_K)
    d = np.asarray(in_d)
    # Input can be list of bbox coords, poly coords, etc.
    # TODO -- Check if point behind camera?
    points_2d = np.asarray(point_list)

    points_2d = points_2d[:, 0:2].astype('float32')
    points2d_undist = np.empty_like(points_2d)
    points_2d = np.expand_dims(points_2d, axis=1)

    result = np.squeeze(cv2.fisheye.undistortPoints(points_2d, K, d))

    K_new = np.asarray(in_K_new)
    fx = K_new[0, 0]
    fy = K_new[1, 1]
    cx = K_new[0, 2]
    cy = K_new[1, 2]

    for i, (px, py) in enumerate(result):
        points2d_undist[i, 0] = px * fx + cx
        points2d_undist[i, 1] = py * fy + cy

    return points2d_undist
    