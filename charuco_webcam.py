import cv2
import numpy as np
from cv2 import aruco
# import matplotlib.pyplot as plt

import glob
import random
import sys


# Note: Pattern generated using charuco_create.py

dictionary = aruco.getPredefinedDictionary(aruco.DICT_4X4_50)
# The pattern was displayed on the monitor. The units below are in m, converted from 
# pixels using monitor specifications.
board = aruco.CharucoBoard((10,8), 0.0161423,0.7*0.0161423,dictionary) #meter units

def read_chessboards(frames):
    all_corners = []
    all_ids = []

    for frame in frames:
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        corners, ids, rejectedImgPoints = cv2.aruco.detectMarkers(gray, dictionary)#Returns the 2d marker
        #corners in the image.(Does not perform pose estimation)

        if len(corners) > 0:
            # This function receives the detected markers and returns the 2D position of the chessboard 
            # corners from a ChArUco board using the detected Aruco markers. If camera parameters 
            # are provided, the process is based in an approximated pose estimation, else it is based 
            # on local homography. Only visible corners are returned. For each corner, its corresponding 
            # identifier is also returned in charucoIds. The function returns the number of interpolated 
            # corners
            ret, c_corners, c_ids = cv2.aruco.interpolateCornersCharuco(corners, ids, gray, board)
            # ret is the number of detected corners
            if ret > 0:
                all_corners.append(c_corners)
                all_ids.append(c_ids)
        else:
            print('Failed!')

    imsize = gray.shape
    return all_corners, all_ids, imsize


def capture_camera(dev_num=0, num=1, mirror=False, size=None):
    frames = []

    cap = cv2.VideoCapture(dev_num)
    # cap = cv2.VideoCapture(dev_num, cv2.CAP_DSHOW)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    # cap.set(cv2.CAP_PROP_AUTO_WB, 0.0) # Disable automatic white balance
    # cap.set(cv2.CAP_PROP_EXPOSURE,5)
    # print(cap.get(cv2.CAP_PROP_EXPOSURE)) 
    while True:
        ret, frame = cap.read()

        if mirror is True:
            frame = cv2.flip(frame, 1)

        if size is not None and len(size) == 2:
            frame = cv2.resize(frame, size)

        # My config applies floating layout for windows named 'Java'
        cv2.imshow('Java', frame)

        k = cv2.waitKey(1)
        if k == 27:  # Esc
            break
        elif k == 10 or k == 32:  # Enter or Space
            frames.append(frame)
            print('Frame captured!')
            if len(frames) == num:
                break

    return frames


def draw_axis(frame, camera_matrix, dist_coeff, board, verbose=True):
    corners, ids, rejected_points = cv2.aruco.detectMarkers(frame, dictionary)
    
    if corners is None or ids is None:
        print("None: Corners and ids")
        return None
    if len(corners) != len(ids) or len(corners) == 0:
        print("Wrong length: Corners and ids")
        return None

    try:
        ret, c_corners, c_ids = cv2.aruco.interpolateCornersCharuco(corners,
                                                                    ids,
                                                                    frame,
                                                                    board)
        ret, p_rvec, p_tvec = cv2.aruco.estimatePoseCharucoBoard(c_corners,
                                                                c_ids,
                                                                board,
                                                                camera_matrix,
                                                                dist_coeff,np.empty(1),np.empty(1))
        
        if p_rvec is None or p_tvec is None:
            print("None: Position")
            return None
        if np.isnan(p_rvec).any() or np.isnan(p_tvec).any():
            print("NaN: Position")
            return None
        cv2.drawFrameAxes(frame,
                        camera_matrix,
                        dist_coeff,
                        p_rvec,
                        p_tvec,
                        0.1)
        # cv2.aruco.drawDetectedCornersCharuco(frame, c_corners, c_ids)
        # cv2.aruco.drawDetectedMarkers(frame, corners, ids)
        # cv2.aruco.drawDetectedMarkers(frame, rejected_points, borderColor=(100, 0, 240))
    except cv2.error:
        return None

    if verbose:
        print('Translation : {0}'.format(p_tvec))
        print('Rotation    : {0}'.format(p_rvec))
        print('Distance from camera: {0} m'.format(np.linalg.norm(p_tvec)))

    return frame


def main():
    # video_dev = int(sys.argv[1])
    frames = capture_camera(0, 5)
    if len(frames) == 0:
        print('No frame captured')
        sys.exit(1)
    all_corners, all_ids, imsize = read_chessboards(frames)
    all_corners = [x for x in all_corners if len(x) >= 4]
    all_ids = [x for x in all_ids if len(x) >= 4]
    ret, camera_matrix, dist_coeff, rvecs, tvecs = cv2.aruco.calibrateCameraCharuco(
        all_corners, all_ids, board, imsize, None, None
    )

    print('> Camera matrix')
    print(camera_matrix)
    print('> Distortion coefficients')
    print(dist_coeff)

    # Real-time axis drawing
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    while True:
        ret, frame = cap.read()
        k = cv2.waitKey(1)
        if k == 27:  # Esc
            break
        axis_frame = draw_axis(frame, camera_matrix, dist_coeff, board, False)
        if axis_frame is not None:
            cv2.imshow('Java', axis_frame)
        else:
            cv2.imshow('Java', frame)
            # cv2.imshow('Java_no_detect', frame)


if __name__ == '__main__':
    main()
