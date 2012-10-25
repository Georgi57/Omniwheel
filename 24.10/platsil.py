import time,math,cv
import robot_com,videoprocessing_platsil

#Initialisation
robot=robot_com.robot()
video_processing=videoprocessing_platsil.VideoProcessing(1,True)
_camera_polling_thread = videoprocessing_platsil.FrameBufferThread()
_camera_polling_thread.start()

cv.NamedWindow( "Camera", cv.CV_WINDOW_AUTOSIZE )

#VARIABLES
last_turn_right=True
turning_frames = 0
target="black"

while True:
        #Get ball coordiates from camera image
        x,y=video_processing.getCoordinates(target)

        #Determine speeds needed
        speed=30

        if x==-1:
            print "Go forward"
            robot.go_forward(speed)
            robot.go_pid(3,0)
            turning_frames=0
        else:
                if turning_frames<3:
                        robot.stop()
                if x<160:
                        print "Right"
                        robot.turn_right(speed/2)
                        last_turn_right=True
                        turning_frames+=1
                else:
                        print "Left"
                        robot.turn_left(speed/2)
                        last_turn_right=False
                        turning_frames+=1

        if cv.WaitKey(1) == 27:
                break

_camera_polling_thread.stop()
cv.DestroyAllWindows()
robot.all_off()
