import SimpleCV,time,math
import robot_com

#Initialisation
robot=robot_com.robot()
ballcolor = (180,45,15)
display = SimpleCV.Display()
cam = SimpleCV.Camera(1,prop_set={"width":320, "height":240})
normaldisplay = True

#VARIABLES
last_turn_right=True
cropped=25 #pixels
no_blobs_frame_counter=0



while display.isNotDone():
        #Display function
        if display.mouseRight:
                normaldisplay = not(normaldisplay)
                print "Display Mode:", "Normal" if normaldisplay else "Segmented"

        #Find blobs
        img = cam.getImage().crop(0,cropped,320,200).dilate()
        dist = img.colorDistance(ballcolor)
        segmented = img-dist
        segmented = segmented.binarize(30).invert().dilate()
        blobs = segmented.findBlobs()
        if blobs:
                no_blobs_frame_counter=0
                #Select the closest blob
                idx=-1
                y=0
                for i in range(len(blobs)):
                    print blobs[i].circleDistance()
                    if blobs[i].maxY()>y:
                        idx=i
                ball=blobs[idx]
                img.drawCircle((ball.x, ball.y), ball.radius(),SimpleCV.Color.GREEN,ball.radius())
                #Get it values (x,y,r,distance,angle)
                x=ball.coordinates()[0]
                y=ball.maxY()+cropped
                r=ball.radius()
                ball_distance=8.7*math.tan(math.radians(50+37.6*((240-y)/240.0)))
                ball_at_angle=0
                if x>=160:
                    ball_at_angle=26.5*((x-160)/160.0)
                else:
                    ball_at_angle=26.5*((160-x)/160.0)
                    
                print "\nCoordinates:",x,y,"Distance to the ball:",ball_distance, "At angle ",ball_at_angle

                #Determine speeds needed
                turn_speed=20
                move_speed=50
                if ball_distance<150:
                        move_speed=int(ball_distance)
                elif ball_distance<30:
                        move_speed=int(ball_distance*2.5)
                
                if x>140 and x<180:
                        if ball_distance<12:
                                robot.go_forward(20)
                                time.sleep(1.5)
                                for i in range(5):
                                        robot.turn_right(30)
                                        time.sleep(1)
                                robot.stop()
                                robot.go_forward(20)
                                break
                                print "Ball in reached"
                        else:
                                robot.go_forward(move_speed)
                                print "Go forward"
                elif x>180:
                        print "Turning RIGHT"
                        robot.go_forward(move_speed)
                        robot.go_pid(1,int(-move_speed*1.2))
                        last_turn_right=True
                elif x<140:
                        print "Turning LEFT"
                        
                        robot.go_forward(move_speed)
                        robot.go_pid(2,int(move_speed*1.2))
                        last_turn_right=False
        else:
                no_blobs_frame_counter+=1
                if no_blobs_frame_counter>=5:
                    print "Turn around"
                    if last_turn_right:
                        robot.turn_right(50)
                    else:
                        robot.turn_left(50)
                    time.sleep(0.2)
                    robot.stop()
                    time.sleep(0.3)
                else:
                    robot.stop()
                
        if normaldisplay:
                img.show()
        else:
                segmented.show()
robot.all_off()
