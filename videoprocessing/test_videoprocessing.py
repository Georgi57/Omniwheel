import videoprocessing
import cv2

"""Initialize camera"""
CV = videoprocessing.VideoProcessing(0,True)

while 1:
    """save image for processing"""
    CV.getImage(show=True)
    """Get coordinates of the target"""
    x,y = CV.getCoordinates("ball",True)
    print x,y
    if x!=-1:
        """If target found, check if it is behind a line"""
        over_line = CV.checkLine(x,y,True)
        print "Over the line: ", over_line

    if cv2.waitKey(1) == 27:
        break
CV.disable()
