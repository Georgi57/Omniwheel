import cv2.cv as cv
import cv2
import numpy as np
import time
import threading

global cam,lock
lock=threading.RLock()

class FrameBufferThread(threading.Thread):
    """
    This is a thread to get rid off camera frame buffer.
    As often as it can, thread gets frames from the camera without processing them.
    """
    running=True
    def run(self):
        global cam, lock
        while self.running:
            lock.acquire()
            try:
                cam.grab()
            finally:
                lock.release()

    def stop(self):
        self.running=False

class VideoProcessing():
    
    def __init__(self, camera_num, debug = False):
        """
        Here all needed variables and data is initialized
        This function is run when starting
        """
        global cam
        #Initialize the camera and its values, Get the first frame
        cam = cv2.VideoCapture(camera_num)
        self.cam_width = cam.set(cv.CV_CAP_PROP_FRAME_WIDTH, 320)
        self.cam_height = cam.set(cv.CV_CAP_PROP_FRAME_HEIGHT, 240)        
    
        self.cam_width = cam.get(cv.CV_CAP_PROP_FRAME_WIDTH)
        self.cam_height = cam.get(cv.CV_CAP_PROP_FRAME_HEIGHT)
        self.debug = debug
        retval, self.frame = cam.read()
        
        self.count = 0
        #Create windows to show videoprocessing
        if self.debug:
            cv2.namedWindow( "Camera", cv.CV_WINDOW_AUTOSIZE )
            cv.MoveWindow('Camera', 450, 0)
            cv2.namedWindow( "Thresholded", cv.CV_WINDOW_AUTOSIZE )
            cv.MoveWindow("Thresholded", 450,350)
            cv2.namedWindow( "contour", cv.CV_WINDOW_AUTOSIZE )
            cv.MoveWindow("contour", 0,350)

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

        #Buffer
        self.buffer = FrameBufferThread()
        self.buffer.daemon = True
        self.buffer.start() 
    
    def nothing(self):
        return None
    
    def disable(self):
        """
        Close all windows and release the camera
        """
        self.buffer.stop()
        cv2.destroyAllWindows()
        cam.release()
    
    def find_intersections(self, A, B):
        ''' (matrix, matrix -> bool'''
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
        if xi[aall(xconds)] and yi[aall(yconds)]:
            return  xi[aall(xconds)], yi[aall(yconds)], True # intersection, don't go!
        return  xi[aall(xconds)], yi[aall(yconds)], False
    
    def color_detection_hsv(self, frame, thresholdminvalues, thresholdmaxvalues):
            ''' (np.array np.uint8 3channel, list of 3 ints, list of 3 ints) -> np.array np.uint8 1channel'''
            ''' Return thresholded_frame according to thresholdmin/maxvalues'''
            hsv_frame=cv2.cvtColor(frame,cv2.COLOR_BGR2HSV) #convert the image to hsv(Hue, Saturation, Value) so its easier to determine the color to track(hue) 
            cv2.blur(hsv_frame, (3,  3), hsv_frame)  # TESTing needed does blurring has an effect. 
            colormin = np.asarray(thresholdminvalues, np.uint8)
            colormax = np.asarray(thresholdmaxvalues, np.uint8)# ball color
            thresholded_frame = cv2.inRange(hsv_frame, colormin, colormax)
            if self.debug:
                cv2.imshow("Thresholded",thresholded_frame)
            return thresholded_frame

    def find_the_biggest_contour(self, thresholded_frame, frame):
            ''' (np.array np.uint8 1channel) -> int, np.array'''
            ''' Return the biggest contourarea and contour itself'''
            frame_contours = cv2.dilate(thresholded_frame, None) #make white areas more visible
            # finding the biggest area
            contours, hierarchy = cv2.findContours(frame_contours, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
            contourareamax = 0
            maxcontour = 0
            greenpixels = False
            for i in contours:
                contourarea = cv2.contourArea(i)
                # check for green
                if contourarea > 1:
                    retval3 = cv2.boundingRect(i)
                    b1 = retval3[0] + retval3[2]
                    b2 = retval3[1] +  retval3[3]
                    #print retval3[0], b1
                    #greenpixels = self.check_for_green_pixels(retval3[0], retval3[1] , b1, b2, frame)
                # remember only the biggest
                if contourarea > contourareamax: # and greenpixels == True:
                    maxcontour = i
                    contourareamax = contourarea
            if self.target == 'ball':
                area = 3
            elif self.target[-1] == 'g':
                area = 50
            if contourareamax > area:
                M = cv2.moments(maxcontour)
                x,y = int(M['m10']/M['m00']), int(M['m01']/M['m00'])
                retval3 = cv2.boundingRect(maxcontour)
                xend = (retval3[0] + retval3[2])
                yend = retval3[1] + retval3[3] *2
                if self.debug:
                    cv2.namedWindow( "contour", cv.CV_WINDOW_AUTOSIZE )
                    cv2.circle(thresholded_frame,(x,y),5,255,-1)
                    cv2.circle(thresholded_frame, (int(x), int(y)), int(retval3[3]), (100, 100, 255))
                    cv2.rectangle(self.frame, (retval3[0], retval3[1]), (xend, yend), (0, 0, 255))
                    cv2.imshow("contour", thresholded_frame)
                    cv2.imshow('Camera', self.frame)
                return x, y
            return -1, -1

    
    def checkLine(self, x, y):
        thresholded_frame = cv2.inRange(self.frame, self.black_threshold_low, self.black_threshold_high)
        lines = np.array([], np.uint8)
        lines = cv2.HoughLines(thresholded_frame, 3, np.pi/30, 30) # TUNING NEEDED! 2 is somekind of distance from coordinate starting point; np.pi/45 is programm is searching lines in every 4th degree ;30 is a threshold
        m,n = thresholded_frame.shape # WHAT DOES IT DO?

        if lines is not None: # if Nonetype then line not found
            ptrobot = float(self.cam_width/2), float(self.cam_height+1) # dependent on camera frame size    
            A = np.matrix(str(ptrobot[0]) + ' ' + str(ptrobot[1]) + '; ' + str(float(x)) + ' ' + str(float(y)))
            for (rho, theta) in lines[0][:2]: # blue for infinite lines (only draw the 2 strongest)
                x0 = np.cos(theta)*rho 
                y0 = np.sin(theta)*rho
                pt1 = ( int(x0 + (m+n)*(-np.sin(theta))), int(y0 + (m+n)*np.cos(theta)))
                pt2 = ( int(x0 - (m+n)*(-np.sin(theta))), int(y0 - (m+n)*np.cos(theta)))
                # A and B are the two lines, each is a two column matrix ---- have to be floats!!!
                B = np.matrix(str(float(pt1[0])) + ' ' + str(float(pt1[1])) + '; ' + str(float(pt2[0])) + ' ' + str(float(pt2[1])))
                interpt1, interpt2, isthereanintersection = self.find_intersections(A, B)
                if isthereanintersection == True:
                    if self.debug:
                        cv2.circle(self.frame, (interpt1, interpt2),20,(0,255,0),2) 
                        cv2.line(self.frame,  pt1, pt2, (255,0,0), 10)
                        cv2.imshow("Camera",self.frame)
                    return True # Sees the ball, but line is disturbing
        return False #Sees the ball and lines aren't disturbing


    def rectmasking(self, frame, x1, y1, x2, y2):
        roiframe = frame[y1:y2, x1:x2]
        if self.debug:
            cv2.namedWindow( "roi", cv.CV_WINDOW_AUTOSIZE )
            cv2.imshow("roi",roiframe)
        return roiframe
                
    
    def check_for_green_pixels(self, x1, y1, x2, y2, frame): # frame = self.frame  ''' not working yet'''
        y2 = y2 + abs(y1 - y2) * 2
        if y2 > frame.shape[1]:
            y2 = frame.shape[1]
        greenpixels = cv2.countNonZero(cv2.inRange(frame[y1:y2, x1:x2], self.green_threshold_low, self.green_threshold_high))
        if greenpixels > 1:
            cv2.rectangle(self.frame, (x1, y1), (x2, y2), (0, 255, 0))
            return True
        return False

    def get_ball_position(self, roiframe):
        return self.find_the_biggest_contour(self.color_detection_hsv(roiframe ,self.ball_threshold_low, self.ball_threshold_high), roiframe)
    def get_goal_position(self, roiframe, goal):
        if goal == 'yellowg':
            return self.find_the_biggest_contour(self.color_detection_hsv(roiframe ,self.yellow_gate_threshold_low, self.yellow_gate_threshold_high), roiframe)
        else:
            return self.find_the_biggest_contour(self.color_detection_hsv(roiframe ,self.blue_gate_threshold_low, self.blue_gate_threshold_high), roiframe)
        
        
    def getCoordinates(self, target="ball"):

        global cam, lock
        lock.acquire()
        try:
            cam.grab()
            self.retval, self.frame = cam.retrieve()
        finally:
            lock.release()
        
        #measuretime = time.time() # for measuring time
        x=-1
        y=-1
        status = False #False = is something disturbing?
        self.target = target
        if target == 'ball':
            section1 = [0, int(self.cam_height*0.7), self.cam_width, self.cam_height] # lower part of pic
            section2 = [0, 0, self.cam_width, int(self.cam_height*0.7)] # upper part of pic # when camera is fixed then sume upper part can be excluded
            # first getCoordinates from lower part of the frame
            sect = section1
            roiframe = self.rectmasking(self.frame, sect[0], sect[1], sect[2], sect[3])
            x, y = self.get_ball_position(roiframe)
            
            # find the center point through a drawn rectangle around the contour
            if x == -1: 
                sect = section2
                roiframe = self.rectmasking(self.frame, sect[0], sect[1], sect[2], sect[3])
                x, y = self.get_ball_position(roiframe)
            #print measuretime - time.time() # for measuring time
            else:
                y = y + self.cam_height*0.7 # because starting coordinate (0,0) isn't taken as fixed point, e.g. every frame has a different (0,0) point
            return x, y, status
        elif target == 'blueg' or target == 'yellowg':
            section1 = [0, 0, self.cam_width, 60] # upper part of pic # when camera is fixed then sume upper part can be excluded
            # first getCoordinates from lower part of the frame
            sect = section1
            roiframe = self.rectmasking(self.frame, sect[0], sect[1], sect[2], sect[3])
            x, y = self.get_goal_position(roiframe, target)
            return x, y, status
        
        elif target == 'lineball':
            #FIND THE BALL  ''' not working yet'''
            section1 = [0, int(self.cam_height*0.7), int(self.cam_width), int(self.cam_height)] # lower part of pic
            section2 = [0, 0, int(self.cam_width), int(self.cam_height*0.7)] # upper part of pic
            # first getCoordinates from lower part of the frame
            sect = section1
            roiframe = self.rectmasking(self.frame, sect[0], sect[1], sect[2], sect[3])
            x, y = self.get_ball_position(roiframe)
            # find the center point through a drawn rectangle around the contour
            
            if x == -1: 
                sect = section2
                roiframe = self.rectmasking(self.frame, sect[0], sect[1], sect[2], sect[3])
                x, y = self.get_ball_position(roiframe)
            #print measuretime - time.time() # for measuring time         
            ''' as there were no balls, then let's not check for lines. '''
            if x == -1:
                return -1, -1, False # Robot doesn't see the ball
            
            #BLACK LINE DETECTION
            #roiframe = 
            
            
            status = self.checkLine(x, y)
        #print measuretime - time.time() # for measuring time
        return x, y, status #Sees the ball + True  if something is disturbing, False if can go to object
