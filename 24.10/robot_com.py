# -*- coding: utf-8 -*-
"""
#
#This file is meant to be used to control the external devices over serial port.
#Motor drivers:    http://digi.physic.ut.ee/mw/index.php/Sise:Liikumismoodul2012
#
"""

import serial,time

class robot():
    def __init__(self):
        #Robot devices
        self.devices=[]
        self.scan_for_devices()
        print ""
        if len(self.devices)==0:
            print "No devices found"
        for i in self.devices:
            print "Device #"+str(i),"Serial port #"
        #Test, if all robot devices are connected
        self.selftest()
        
    def scan_for_devices(self):
        #scan for available ports.
        #Returns list with device id, port number and the opened port itself.
        for i in range(256):
            try:
                s = serial.Serial("/dev/ttyACM"+str(i),timeout=1,parity=serial.PARITY_NONE,baudrate=115200)
                s.write("\n")
                id_string=s.readline()
                s.write("?\n")
                id_string=s.readline()
                mootor_id=int(id_string[id_string.rfind(":")+1])
                self.devices.append([mootor_id,i,s])
            except serial.SerialException:
                pass

    def selftest(self):
        #A small robot device test and count
        print "\nSELFTEST:"
        found=[0,0,0]
        for dev in self.devices:
            found[dev[0]-1]=1
        all_in_place=True
        for dev_in_place in found:
            if not dev_in_place:
                all_in_place=False
                print "ERROR : Device " +str()+" are missing"
        if sum(found)==len(found):
            print "Sucessful"
        

    def send_command(self,dev,command,get_answer=False):
        #Sending a command to an external device through the COM port.
        complited=False
        answer="no answer"
        for i in self.devices:
            if i[0]==dev:
                i[2].write(command)
                if get_answer:
                    answer=i[2].readline()
                complited=True
        if not complited:
            print "Cannot send the command '" + command[:-1] + "' because the device "+str(dev)+" is missing."
        if get_answer:
            return answer

    #TURN OFF ALL ROBOT DEVICES

    def all_off(self):
        print "\nStopping motors"
        self.auto_off(1,1)
        self.auto_off(2,1)
        self.auto_off(3,1)
        print "Turning of all external devices"
        for dev in self.devices:
            dev[2].close()
        print "Closing this program"
        del self

    #DIRECT COMMAND TO MOTORS THROUGH SERIAL PORT

    def go_pid(self,dev,speed):
        #Motor speed -190..190
        self.send_command(dev,"sd"+str(speed)+"\n")

    def go_no_pid(self,dev,speed):
        #Motor speed --255..255
        self.send_command(dev,"wl"+str(speed)+"\n")

    def change_direction(self,dev,direction):
        #Motor direction 0 or 1
        self.send_command(dev,"dr"+str(direction)+"\n")

    def pid_control(self,dev,status):
        #Turn PID control on(1) or off(0)
        self.send_command(dev,"pd"+str(status)+"\n")

    def show_speed(self,dev):
        #Show motor speed
        speed=self.send_command(dev,"s\n",True)
        print "Mootor "+str(dev)+" speed: "+str(speed)
        return speed

    def show_id(self,dev):
        #Show motor id
        motor_id=self.send_command(dev,"?\n",True)
        print "Motor id is: "+str(motor_id)
        return motor_id

    def auto_speed_send(self,dev,status):
        #Send speed of the motor automatically with 62.5 Hz (0 or 1)
        self.send_command(dev,"gs"+str(status)+"\n")

    def auto_off(self,dev,status):
        #Motor turns itself off after 1.6 seconds after the last speed command.
        #It can be turned of: 0 or 1
        self.send_command(dev,"fs"+str(status)+"\n")

    def ball_at_dribbler(self):
        #Control if the ball is at the dribbler
        status=self.send_command(3,"ds\n",True)
        if status=="0\n":
            return True
        else:
            return False

    #ROBOT MOVEMENTS

    #
    #Speed is in per cents of the maximum speed.
    #
    def speed_acceptable(self,speed):
        if speed>=0 and speed<=160:
            return True
        else:
            print "Not acceptable speed: "+str(speed)+". Should be between 0 and 100"
            return False

    def stop(self):
        self.go_pid(1,0)
        self.go_pid(2,0)
        self.go_pid(3,0)
    
    def go_forward(self,speed):
        if self.speed_acceptable(speed):
            self.go_pid(1,-speed)
            self.go_pid(2,speed)

    def go_backward(self,speed):
        if self.speed_acceptable(speed):
            self.go_pid(1,speed)
            self.go_pid(2,-speed)

    def turn_left(self,speed):
        if self.speed_acceptable(speed):
            self.go_pid(1,speed)
            self.go_pid(2,speed)
            self.go_pid(3,speed)

    def turn_right(self,speed):
        if self.speed_acceptable(speed):
            self.go_pid(1,-speed)
            self.go_pid(2,-speed)
            self.go_pid(3,-speed)

    def go_left(self,speed):
        if self.speed_acceptable(speed):
            self.go_pid(1,speed)
            self.go_pid(2,speed)
            self.go_pid(3,-int(1.7*speed))

    def go_right(self,speed):
        if self.speed_acceptable(speed):
            self.go_pid(1,-speed)
            self.go_pid(2,-speed)
            self.go_pid(3,int(1.7*speed))
