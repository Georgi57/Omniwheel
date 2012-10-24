import cv2.cv as cv
import cv2
import time

"""Create window"""
cv2.namedWindow( "Camera", cv.CV_WINDOW_AUTOSIZE )

"""Initialize camera"""
cam = cv2.VideoCapture(0)

while True:
    """Get an image from the camera"""
    retval,  frame = cam.read()
    """Show image, function returned any"""
    if retval:
        cv2.imshow( "Camera", frame )
    print "Press ESC to exit"
    if cv2.waitKey(50) == 27:
        break

cv2.destroyAllWindows()

