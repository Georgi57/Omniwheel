import time,math,cv
import robot_com,videoprocessing

use_smallScreen = False

#Initialisation
robot=robot_com.robot()
#camera_processing=get_coordinates_SimpleCV.color_recognition_SimpleCV(1)
video_processing=videoprocessing.VideoProcessing(1,use_smallScreen)
_camera_polling_thread = videoprocessing.FrameBufferThread()
_camera_polling_thread.start()

cv.NamedWindow( "Camera", cv.CV_WINDOW_AUTOSIZE )

#VARIABLES
last_turn_right=True
no_blobs_frame_counter=0
ball_at_dribbler=False

screen_x = 640.0
screen_y = 480.0
if use_smallScreen:
        screen_x=320.0
        screen_y=240.0

very_near_ball=15

while True:
        
        #Control if ball is under the dribbler
        if robot.ball_at_dribbler():
                ball_at_dribbler=True
        else:
                ball_at_dribbler=False

        #Get ball coordiates from camera image
        if not ball_at_dribbler:
                x,y=video_processing.getCoordinates("ball")
        else:
                x,y=video_processing.getCoordinates("yellow gate")

        ball_distance=8.7*math.tan(math.radians(50+37.6*((screen_y-y)/screen_y)))
        ball_at_angle=0
        if x>=screen_x:
            ball_at_angle=26.5*((x-screen_x)/screen_x)
        else:
            ball_at_angle=26.5*((screen_x-x)/screen_x)
            
        print "\nCoordinates:",x,y,"Distance to the ball:",ball_distance, "At angle ",ball_at_angle

        #Determine speeds needed
        speed=50
        
        if ball_distance<40:
                speed=int(ball_distance)
        elif ball_distance<150:
                speed=int(ball_distance/2)

        print speed
        
        if x==-1:
                """
                Find the target by turning around
                """
                no_blobs_frame_counter+=1
                if no_blobs_frame_counter>=7:
                        if not ball_at_dribbler:
                                """
                                Searching for the ball
                                """
                                if last_turn_right:
                                        robot.turn_right(50)
                                else:
                                        robot.turn_left(50)
                                time.sleep(0.15)
                                robot.stop()
                                time.sleep(0.1)
                        else:
                                """
                                Searching for the gate
                                """
                                if last_turn_right:
                                        robot.turn_right(20)
                                else:
                                        robot.turn_left(20)
                elif no_blobs_frame_counter>3:
                        robot.stop()

        else:
                """
                If target found: turn or go to it.
                """
                if ball_distance<=very_near_ball:
                        """If not, turn to it"""
                        if x>=screen_x*0.7:
                                robot.turn_right(50)
                                time.sleep(0.01*ball_at_angle/1.0)
                                robot.stop()
                                last_turn_right=True
                        elif x<screen_x*0.3:
                                robot.turn_left(50)
                                time.sleep(0.01*ball_at_angle/1.0)
                                robot.stop()
                                last_turn_right=False
                        
                        else:
                                """If the ball is in the center just grab it"""
                                robot.go_forward(30)
                                robot.go_pid(3,0)
                                time.sleep(1.0)
                else:
                        """
                        But if the ball is far enough, drive to it
                        """
                        if x<=screen_x*0.4:
                                """Drive a little to the left"""
                                robot.go_pid(1,-speed)
                                robot.go_pid(2,speed+int(ball_at_angle/ball_distance)*2)
                                robot.go_pid(3,-int(ball_at_angle/ball_distance)*2)
                        elif x>screen_x*0.6:
                                """Drive a little to the right"""
                                robot.go_pid(1,-speed-int(ball_at_angle/ball_distance)*2)
                                robot.go_pid(2,speed)
                                robot.go_pid(3,int(ball_at_angle/ball_distance)*2)
                        else:
                                robot.go_forward(speed)
                                
                        
        if cv.WaitKey(1) == 27:
                break

_camera_polling_thread.stop()
cv.DestroyAllWindows()
robot.all_off()
