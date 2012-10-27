import cv2.cv as cv
import cv2

"""Create window"""
cv2.namedWindow( "Camera", cv.CV_WINDOW_AUTOSIZE )

"""Initialize camera"""
cam = cv2.VideoCapture(0)

while True:
    """Get an image from the camera"""
    retval,  frame = cam.read()
    """
    cam.set(cv.CV_CAP_PROP_POS_FRAMES,10)
    cam.set(cv.CV_CAP_PROP_FPS,10)
    cam.set(cv.CV_CAP_PROP_FORMAT,10)
    cam.set(cv.CV_CAP_PROP_MODE,10)
    cam.set(cv.CV_CAP_PROP_BRIGHTNESS,10)
    cam.set(cv.CV_CAP_PROP_CONTRAST,10)
    cam.set(cv.CV_CAP_PROP_SATURATION,10)
    cam.set(cv.CV_CAP_PROP_HUE,10)
    cam.set(cv.CV_CAP_PROP_GAIN,10)
    cam.set(cv.CV_CAP_PROP_EXPOSURE,10)
    cam.set(cv.CV_CAP_PROP_CONVERT_RGB,10)
    """

    print cam.get(cv.CV_CAP_PROP_POS_FRAMES)
    print cam.get(cv.CV_CAP_PROP_FPS)
    print cam.get(cv.CV_CAP_PROP_FORMAT)
    print cam.get(cv.CV_CAP_PROP_MODE)
    print cam.get(cv.CV_CAP_PROP_BRIGHTNESS)
    print cam.get(cv.CV_CAP_PROP_CONTRAST)
    print cam.get(cv.CV_CAP_PROP_SATURATION)
    print cam.get(cv.CV_CAP_PROP_HUE)
    print cam.get(cv.CV_CAP_PROP_GAIN)
    print cam.get(cv.CV_CAP_PROP_EXPOSURE)
    print cam.get(cv.CV_CAP_PROP_CONVERT_RGB)
    """Show image, function returned any"""
    if retval:
        cv2.imshow( "Camera", frame )
    print "Press ESC to exit"
    if cv2.waitKey(50) == 27:
        break

cv2.destroyAllWindows()
cam.release()

