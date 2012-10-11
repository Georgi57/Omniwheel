import robot_com
import time
robot=robot_com.robot()

action=6
robot.pid_control(1,1)
robot.pid_control(2,1)
robot.pid_control(3,1)

if action==1:#Go forward
    print "\nGoing forward"
    robot.go_pid(1,-80)
    robot.go_pid(2,80)
    time.sleep(1)
    robot.go_pid(1,-170)
    robot.go_pid(2,170)
    time.sleep(1)
elif action==2:#Go backward
    print "\nGoing backward"
    robot.go_pid(1,70)
    robot.go_pid(2,-70)
elif action==3:#Go turn left
    print "\nTurning LEFT"
    robot.go_pid(1,10)
    robot.go_pid(2,10)
    robot.go_pid(3,10)
elif action==4:#Go turn right
    print "\nTurning RIGHT"
    robot.go_pid(1,-4)
    robot.go_pid(2,-4)
    robot.go_pid(3,-4)
elif action==5:#Risti paremale
    print "\nRisti paremale"
    for i in range(10):
        robot.go_pid(1,-20)
        robot.go_pid(2,-20)
        robot.go_pid(3,34)
        time.sleep(0.5)
    robot.stop()

else:
    print "proov"
    for i in range(10):
        robot.turn_right(30)
        time.sleep(0.5)
    robot.stop()
    #robot.go_pid(1,0)
    #robot.go_pid(2,0)
    #robot.go_pid(3,0)
    


"""
for i in range(100):
    print robot.show_speed(1)
    print robot.show_speed(2)
    print robot.show_speed(3)
"""

robot.go_pid(1,0)
robot.go_pid(2,0)
robot.go_pid(3,0)

robot.all_off()

