import cv2
from cv2 import aruco

# The Charuco board uses the ratio bw the squarelength and marker length.
# It can be in m or pixels as units, as long as it is consistent.
# Since ensuring flatness of the image is important for calibration,
# it is best to calibrate using a monitor. Working in pixels has the
# added advantage of being easily translatable to the image using the generateImage()
# function which takes pixels.
def createBoard():
    dictionary = aruco.getPredefinedDictionary(aruco.DICT_4X4_50)
    # board = aruco.CharucoBoard((10,8), 0.015,0.011,dictionary)
    board = aruco.CharucoBoard((10,8), 100,70,dictionary)
    board_image = board.generateImage((1020,820), 10, 1) #needs pixels
    cv2.imshow("board", board_image)
    key = cv2.waitKey(1000)
    cv2.imwrite("charuco_board.png", board_image)


if __name__ == "__main__":
    createBoard()
