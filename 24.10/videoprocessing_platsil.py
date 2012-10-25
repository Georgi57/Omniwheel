"""
Here should be implement whole videoprocessing
"""
import cv,cv2,SimpleCV
import threading

global cam, lock
lock=threading.RLock()

class FrameBufferThread(threading.Thread):
    """
    This is a thread to get rid off camera frame buffer.
    As often as it can, thread gets frames from the camera without processing them.
    """
    running=True
    def run(self):
        global _camera, lock
        while self.running:
            lock.acquire()
            try:
                cv.GrabFrame(cam)
            finally:
                lock.release()

    def stop(self):
        self.running=False

class VideoProcessing():
    
    def __init__(self,camera_num,smallResolution=False):
        """Initialize and configure camera"""
        global cam
        cam=cv.CreateCameraCapture(camera_num)
        if smallResolution:
            cv.SetCaptureProperty(cam,cv.CV_CAP_PROP_FRAME_WIDTH,320)
            cv.SetCaptureProperty(cam,cv.CV_CAP_PROP_FRAME_HEIGHT,240)
            #cv.SetCaptureProperty(self.cam,cv.CV_CAP_PROP_FPS,30)

        """Create some image variables for using in the processing so that they would not have to be initialized running"""
        size = (640,480)
        if smallResolution:
            size = (320,240)
            
        self.hsv_frame = cv.CreateImage(size, 8, 3)
        self.thresholded_frame =  cv.CreateImage(size, 8, 1)

        """
        Import the threshold values that are set by the thresholds.py program
        """
        f = open('thresholdvalues.txt',  'r')
        thresholdvalues = f.read()
        f.close()
        clrs=thresholdvalues.split()
        for i in range(len(clrs)):
            clrs[i]=int(clrs[i])
        """Choose the thresholds(variable names speak for them self)"""
        self.ball_threshold_low=(clrs[0],clrs[1],clrs[2])
        self.ball_threshold_high=(clrs[3],clrs[4],clrs[5])

        self.blue_gate_threshold_low=(clrs[6],clrs[7],clrs[8])
        self.blue_gate_threshold_high=(clrs[9],clrs[10],clrs[11])

        self.yellow_gate_threshold_low=(clrs[12],clrs[13],clrs[14])
        self.yellow_gate_threshold_high=(clrs[15],clrs[16],clrs[17])

        self.black_threshold_low=(clrs[18],clrs[19],clrs[20])
        self.black_threshold_high=(clrs[21],clrs[22],clrs[23])

        self.white_threshold_low=(clrs[24],clrs[25],clrs[26])
        self.white_threshold_high=(clrs[27],clrs[28],clrs[29])

        self.green_threshold_low=(clrs[30],clrs[31],clrs[32])
        self.green_threshold_high=(clrs[33],clrs[34],clrs[35])
        
    def getCoordinates(self,target="ball",debug=False):
        """
        This function will return the best coordinates found by thresholding the received image
        by the chosen threshold.
        """
        """Get the latest frame from the camera"""
        global cam, lock
        lock.acquire()
        try:
            cv.GrabFrame(cam)
            frame = cv.RetrieveFrame(cam)
        finally:
            lock.release()
        """Initialize the coordinates to -1, which means that the object is not found"""
        x=-1
        y=-1

        """Prepair image for thresholding"""
        #cv.Smooth(thresholded_frame, thresholded_frame, cv.CV_GAUSSIAN, 5, 5)
        cv.Smooth(frame, frame, cv.CV_BLUR, 3);  
        cv.CvtColor(frame, self.hsv_frame, cv.CV_BGR2HSV) 

        """Threshold the image according to the chosen thresholds"""
        if target == "ball":
            cv.InRangeS(self.hsv_frame, self.ball_threshold_low, self.ball_threshold_high, self.thresholded_frame)
        elif target == "blue gate":
            cv.InRangeS(self.hsv_frame, self.blue_gate_threshold_low, self.blue_gate_threshold_high, self.thresholded_frame)
        elif target == "yellow gate":
            cv.InRangeS(self.hsv_frame, self.yellow_gate_threshold_low, self.yellow_gate_threshold_high, self.thresholded_frame);
        elif target == "black":
            cv.InRangeS(self.hsv_frame, self.black_threshold_low, self.black_threshold_high, self.thresholded_frame);
        elif target == "white":
            cv.InRangeS(self.hsv_frame, self.white_threshold_low, self.white_threshold_high, self.thresholded_frame);
        else:#green
            cv.InRangeS(self.hsv_frame, self.green_threshold_low, self.green_threshold_high, self.thresholded_frame);

        """Now use some function to find the object"""
        blobs_image = SimpleCV.Image(self.thresholded_frame)
        blobs = blobs_image.findBlobs()
        if blobs:
            for i in range(len(blobs)):
                line = blobs[i]
                angle = line.angle()
                pos_x,pos_y = line.coordinates()
                if line.maxY()>100:
                    y=line.maxY()
                    if angle>0:
                        x=line.maxX()
                    else:
                        x=line.minX()
                    break
                
        if debug:            
            cv.ShowImage( "Camera", self.thresholded_frame )
            #thresholded_frame=SimpleCV.Image(thresholded_frame)
            #blobs_image.show()
                
        return x,y
