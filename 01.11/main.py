import time,math,cv
import robot_com,videoprocessing

use_smallScreen = True
debug = True

#Initialisation
robot=robot_com.robot()
video_processing=videoprocessing.VideoProcessing(1,debug)

#VARIABLES
last_turn_right=True
no_blobs_frame_counter=0
ball_at_dribbler=False

screen_x = 640.0
screen_y = 480.0
if use_smallScreen:
        screen_x=320.0
        screen_y=240.0

very_near_ball=20

while True:
        t=time.time()
        
        #Control if ball is under the dribbler
        if robot.ball_at_dribbler():
                ball_at_dribbler=True
        else:
                ball_at_dribbler=False

        x=-1
        y=-1

        #Get ball coordiates from camera image
        if not ball_at_dribbler:
                x,y,over_line=video_processing.getCoordinates("ball")
                if over_line:
                        x=-1
                        y=-1
        else:
                x,y,over_line=video_processing.getCoordinates("yellowg")

        ball_distance=8.7*math.tan(math.radians(50+37.6*((screen_y-y)/screen_y)))
        ball_at_angle=0
        if x>=screen_x:
            ball_at_angle=26.5*((x-screen_x)/screen_x)
        else:
            ball_at_angle=26.5*((screen_x-x)/screen_x)
            
        print "\nCoordinates:",x,y,"Distance to the ball:",ball_distance, "At angle ",ball_at_angle

        #Determine speeds needed
        speed=50
        
        if ball_distance<50:
                speed=int(ball_distance)
        elif ball_distance<150:
                speed=int(ball_distance/2)
        
        if x==-1:
                """
                Find the target by turning around
                """
                no_blobs_frame_counter+=1
                if no_blobs_frame_counter>150:
                        if not video_processing.checkLine(160,120):
                                robot.go_forward(50)
                                robot.go_pid(3,0)
                                time.sleep(1)
                                no_blobs_frame_counter=0
                elif no_blobs_frame_counter>=5:
                        if not ball_at_dribbler:
                                """
                                Searching for the ball
                                """
                                if last_turn_right:
                                        robot.turn_right(5)
                                else:
                                        robot.turn_left(5)
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
                if no_blobs_frame_counter>3:
                        no_blobs_frame_counter=0
                        robot.stop()
                """
                If target found: Go to it
                """
                if not ball_at_dribbler:
                        if ball_distance<15:
                                if x>=screen_x*0.8:
                                        robot.turn_right(12)
                                        robot.go_pid(2,5)
                                        last_turn_right=True
                                elif x<screen_x*0.2:
                                        robot.turn_left(12)
                                        robot.go_pid(1,-5)
                                        last_turn_right=False
                                else:
                                        """If the ball is in the center just grab it"""
                                        robot.go_forward(20)
                                        robot.go_pid(3,0)
                        elif ball_distance<30:
                                if x>=screen_x*0.55:
                                        robot.go_pid(1,-20)
                                        robot.go_pid(2,15)
                                        robot.go_pid(3,5)
                                        last_turn_right=True
                                elif x<screen_x*0.45:
                                        robot.go_pid(1,-15)
                                        robot.go_pid(2,20)
                                        robot.go_pid(3,-5)
                                        last_turn_right=False
                                else:
                                        robot.go_forward(20)
                                        robot.go_pid(3,0)
                        else:
                                if x>=screen_x*0.55:
                                        robot.go_pid(1,-40)
                                        robot.go_pid(2,35)
                                        robot.go_pid(3,5)
                                        last_turn_right=True
                                elif x<screen_x*0.45:
                                        robot.go_pid(1,-35)
                                        robot.go_pid(2,40)
                                        robot.go_pid(3,-5)
                                        last_turn_right=False
                                else:
                                        robot.go_forward(30)
                                        robot.go_pid(3,0)
                else:
                        """If searching for the gate"""
                        if x>=screen_x*0.6:
                                robot.turn_right(5)
                                last_turn_right=True
                        elif x<screen_x*0.4:
                                robot.turn_left(5)
                                last_turn_right=False
                        else:
                                robot.stop()
                        
        if cv.WaitKey(1) == 27:
                break

        print time.time()-t

video_processing.disable()
robot.all_off()
