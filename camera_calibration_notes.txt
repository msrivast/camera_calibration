Camera Calibration
------------------

1. An interesting estimation problem in which the goal is to determine the camera's intrinsic(focal lenth, image centers (cx cy), distortion (radial(barrel and pincussion)) and extrinsic(Homogeneous T_cw(rotation and position of the world frame wrt the camera frame). It is a common misconception and often repeated in OpenCVs Aruco ducumentation that this is T_wc or the camera's pose wrt the world frame but that's not true.). 

2. There are 3 frames involved -
    1. camera frame which projects the object onto the image plane separated by f
    2. image frame - intrinsic parameters, has pixel units with top-left corner zeros
    3. world frame
https://www.cse.iitd.ac.in/~suban/vision/geometry/node38.html

3. We have 11 unknowns and projection of each point gives two equations.
Therefore, 6 point correspondences are sufficient to solve for intrinsic and extrinsic
params, assuming no distortion.

ASIDE: When there is distortion, the Tsai model (https://www.cse.iitd.ac.in/~suban/vision/geometry/node40.html) -
Pinhole + lens distrotion can be used. The parameters of this model can be estimated using either planar or non-planar object points with the latter requiring 8 non-planar point correspondences(7+1) https://www.cse.iitd.ac.in/~suban/vision/geometry/node41.html. By making smart choices for the first pass e.g. using pixel units for focal length, assuming zero distortion this non-linear problem can be transformed into a set of linear equations that can be solved algebraically(or f and t_y can be linear least squares estimated after R is solved for) and that solution is used as an intial guess for the non-linear optimization problem that minimizes the reprojection error while including lens distortion effects and pixel dimensions.
(Calibration with planar object points can be done with fewer points but cannot estimate s_x, XY scale parameter)

4. OpenCV's camera calib3d library uses Zhang's method(https://www.ipb.uni-bonn.de/html/teaching/photo12-2021/2021-pho1-22-Zhang-calibration.pptx.pdf) and comes with support for planar calibration target in the form of image processing for chessboard detection. The Aruco library can perform calibration using Aruco marker corners or ChAruco corners in respective boards. The method estimates the full intrinsic parameter matrix and target pose using atleast 4 point correspondences(there can be ambiguity with 4, see remark below)! That's a total of 8 pieces of information to estimate 11+ params. As shown in the aside above, there is structure in the problem that can be smartly exploited.

5. When you detect a ChArUco board, what you are actually detecting is each of the chessboard corners of the board.
Each corner on a ChArUco board has a unique identifier (id) assigned. These ids go from 0 to the total number of corners in the board.

6. Calibrating on a monitor avoids the potential scale mismatch and lack of flatness of the pattern. In my case, my laptop's monitor had a 120hz refresh rate which avoided banding and resulted in pretty accurate calibration.

It is important to remark that the estimation of the pose using only 4 coplanar points is subject to ambiguity. In general, the ambiguity can be solved, if the camera is near to the marker. However, as the marker becomes small, the errors in the corner estimation grows and ambiguity comes as a problem. Try increasing the size of the marker you're using, and you can also try non-symmetrical (aruco_dict_utils.cpp) markers to avoid collisions. Use multiple markers (ArUco/ChArUco/Diamonds boards) and pose estimation with solvePnP() with the SOLVEPNP_IPPE_SQUARE option.
