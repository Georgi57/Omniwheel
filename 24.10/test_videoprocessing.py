import videoprocessing
import cv

Process = videoprocessing.VideoProcessing(1)
_camera_polling_thread = videoprocessing.FrameBufferThread()
_camera_polling_thread.start()

cv.NamedWindow( "Camera", cv.CV_WINDOW_AUTOSIZE )

while 1:
    print Process.getCoordinates("ball",True)
    
    if cv.WaitKey(1) == 27:
        break

_camera_polling_thread.stop()
cv.DestroyAllWindows()
