"""
Here should be implement color recognition
"""
import cv2.cv as cv
import cv2
import numpy as np
import time

class VideoProcessing():
    def __init__(self,camera_num,debug=False):
        """
        Here all needed variables and data is initialized
        This function is run when starting
        """
        #Initialize the camera and its values, Get the first frame
        self.cam = cv2.VideoCapture(camera_num)
        self.cam_width = self.cam.get(cv.CV_CAP_PROP_FRAME_WIDTH)
        self.cam_height = self.cam.get(cv.CV_CAP_PROP_FRAME_HEIGHT)
        
        self.retval, self.frame = self.cam.read()

        #Create windows to show videoprocessing
        if debug:
            cv2.namedWindow( "Camera", cv.CV_WINDOW_AUTOSIZE )
            cv2.namedWindow( "Thresholded", cv.CV_WINDOW_AUTOSIZE )

        """
        Import the threshold values that are set by the thresholds.py program
        """
        thresholdvalues=""
        try:
            f = open('thresholdvalues.txt',  'r')
            thresholdvalues = f.read()
            f.close()
        except:
            print "No threshold values found. Creating blank list"
            for i in range(36):
                thresholdvalues+="0 "

        clrs=thresholdvalues.split()
        for i in range(len(clrs)):
            clrs[i]=int(clrs[i])
        
        #Choose the thresholds (variable names speak for them self)
        self.ball_threshold_low =        np.asarray([clrs[0],clrs[1],clrs[2]], np.uint8)
        self.ball_threshold_high =       np.asarray([clrs[3],clrs[4],clrs[5]], np.uint8)

        self.blue_gate_threshold_low =   np.asarray([clrs[6],clrs[7],clrs[8]], np.uint8)
        self.blue_gate_threshold_high =  np.asarray([clrs[9],clrs[10],clrs[11]], np.uint8)

        self.yellow_gate_threshold_low = np.asarray([clrs[12],clrs[13],clrs[14]], np.uint8)
        self.yellow_gate_threshold_high =np.asarray([clrs[15],clrs[16],clrs[17]], np.uint8)

        self.black_threshold_low =       np.asarray([clrs[18],clrs[19],clrs[20]], np.uint8)
        self.black_threshold_high =      np.asarray([clrs[21],clrs[22],clrs[23]], np.uint8)

        self.white_threshold_low =       np.asarray([clrs[24],clrs[25],clrs[26]], np.uint8)
        self.white_threshold_high =      np.asarray([clrs[27],clrs[28],clrs[29]], np.uint8)

        self.green_threshold_low =       np.asarray([clrs[30],clrs[31],clrs[32]], np.uint8)
        self.green_threshold_high =      np.asarray([clrs[33],clrs[34],clrs[35]], np.uint8)

    def getImage(self,show=False):
        """
        Just fetching a frame from the camera.
        Show it, if you would like to see. Default - don't show
        """
        self.retval, self.frame = self.cam.read()
        if self.retval and show:
            cv2.imshow( "Camera", self.frame)

    def disable(self):
        """
        Close all windows and release the camera
        """
        cv2.destroyAllWindows()
        self.cam.release()
    
    def findIntersections(self, A, B):
        """
        Given two lines, function determines if these two lines intersect
        """
        # min, max and all for arrays
        amin = lambda x1, x2: np.where(x1<x2, x1, x2)
        amax = lambda x1, x2: np.where(x1>x2, x1, x2)
        aall = lambda abools: np.dstack(abools).all(axis=2)
        slope = lambda line: (lambda d: d[:,1]/d[:,0])(np.diff(line, axis=0))
        x11, x21 = np.meshgrid(A[:-1, 0], B[:-1, 0])
        x12, x22 = np.meshgrid(A[1:, 0], B[1:, 0])
        y11, y21 = np.meshgrid(A[:-1, 1], B[:-1, 1])
        y12, y22 = np.meshgrid(A[1:, 1], B[1:, 1])

        m1, m2 = np.meshgrid(slope(A), slope(B))
        m1inv, m2inv = 1/m1, 1/m2

        yi = (m1*(x21-x11-m2inv*y21) + y11)/(1 - m1*m2inv)
        xi = (yi - y21)*m2inv + x21

        xconds = (amin(x11, x12) < xi, xi <= amax(x11, x12), 
                  amin(x21, x22) < xi, xi <= amax(x21, x22) )
        yconds = (amin(y11, y12) < yi, yi <= amax(y11, y12),
                  amin(y21, y22) < yi, yi <= amax(y21, y22) )

        return xi[aall(xconds)], yi[aall(yconds)]

    def getCoordinates(self,target="ball",debug=False):
        """
        This function searches for the target (ball/yellow gate/blue gate).
        It's done by the using thresholds and contour searching.
        Counter with the biggest area is chosen.

        First thresholding
        """
        #Initial ball position (not on the image) 
        x=-1
        y=-1
        
        #Convert to HSV space and blur the image to reduce color noise 
        hsv_frame=cv2.cvtColor(self.frame,cv2.COLOR_BGR2HSV)
        cv2.blur(hsv_frame, (1,  1), hsv_frame)

        if target == "ball":
            self.thresholded_frame = cv2.inRange(hsv_frame, self.ball_threshold_low, self.ball_threshold_high)
        elif target == "blue gate":
            self.thresholded_frame = cv2.inRange(hsv_frame, self.blue_gate_threshold_low, self.blue_gate_threshold_high)
        else: #yellow gate
            self.thresholded_frame = cv2.inRange(hsv_frame, self.yellow_gate_threshold_low, self.yellow_gate_threshold_high)

        #Erode the image (what ever it means)
        frame_contours = cv2.erode(self.thresholded_frame, None)

        if debug:
            cv2.imshow("Thresholded",self.thresholded_frame)

        """
        Finding a contour with the biggest area
        """
        contours, hierarchy = cv2.findContours(frame_contours, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
        contourareamax = 0
        maxcontour = 0
        for i in contours:
            contourarea = cv2.contourArea(i)
            if contourarea > contourareamax:
                maxcontour = i
                contourareamax = contourarea
            #Find the center point of the contour
            try:
                if contourarea > 5:
                    center, radius = cv2.minEnclosingCircle(maxcontour)
                    #cv2.boundingRect(contourareamax)
                    x, y = center
                    if debug:
                        cv2.circle(self.frame, (int(x), int(y)), int(radius), (100, 100, 255))
            except:
                print "Can't find the minimum enclosing circle"    

        if debug:
            cv2.imshow("Camera",self.frame)

        return x,y

    def checkLine(self,x,y,debug=False):
        """
        Black line detection

        This function searches for black lines and controls if given coordinates are behind it.
        """   
        thresholded_frame = cv2.inRange(self.frame, self.black_threshold_low, self.black_threshold_high)
        #Hough lines, should try some other variables
        lines = cv2.HoughLines(thresholded_frame, 2, np.pi/90, 30) # 30 is a threshold
        m,n = thresholded_frame.shape
        try:
            if lines:
                """
                If some lines are found, try for intersections all of them
                """
                for (rho, theta) in lines[0][:5]:
                    # blue for infinite lines (only draw the 5 strongest)
                    x0 = np.cos(theta)*rho 
                    y0 = np.sin(theta)*rho
                    pt1 = ( int(x0 + (m+n)*(-np.sin(theta))), int(y0 + (m+n)*np.cos(theta)) )
                    pt2 = ( int(x0 - (m+n)*(-np.sin(theta))), int(y0 - (m+n)*np.cos(theta)) )
                    if debug:
                         cv2.line(frame, pt1, pt2, (255,0,0), 2)
                         cv2.imshow("Thresholded",thresholded_frame)
                
                    ptrobot = float(self.cam_width/2), float(self.cam_height+1) # dependent on camera frame size        
                    # A and B are the two lines, each is a two column matrix ---- have to be floats!!!
                    A = np.matrix(str(ptrobot[0]) + ' ' + str(ptrobot[1]) + '; ' + str(x) + ' ' + str(y))
                    B = np.matrix(str(float(pt1[0])) + ' ' + str(float(pt1[1])) + '; ' + str(float(pt2[0])) + ' ' + str(float(pt2[1])))

                    intersection = self.findIntersections(A, B)
                    if not intersection[0] and not intersection[1]:
                        return False # no intersection
                    else:
                        return True # intersection
        except:
            return False


