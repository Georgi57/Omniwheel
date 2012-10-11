# -*- coding: utf-8 -*-
"""
#
#This file is meant to be used to control the external devices over serial port.
#Motor drivers:    http://digi.physic.ut.ee/mw/index.php/Sise:Liikumismoodul2012
#
"""

import serial

class robot():
    def __init__(self,debug=False):
        #Debug mode
        self.debug=debug
        #Robot devices
        self.devices=[]
        self.scan_for_devices()
        print "\n[Device number, Serial port number]"
        if len(self.devices)==0:
            print "No devices found"
        for i in self.devices:
            print i
        #Test, if all robot devices are connected
        self.selftest()
        robot.pid_control(1,1)
        robot.pid_control(2,1)
        robot.pid_control(3,1)
        
    def scan_for_devices(self):
        #scan for available ports.
        #Returns list with device id, port number and the opened port itself.
        for i in range(256):
            try:
                s = serial.Serial(i,timeout=1,parity=serial.PARITY_NONE,baudrate=115200)
                s.write("?\n")
                id_string=s.readline()
                mootor_id=int(id_string[id_string.rfind(":")+1])
                self.devices.append([mootor_id,i,s])
            except serial.SerialException:
                pass

    def selftest(self):
        #A small robot device test and count
        print "\nSELFTEST:"
        counter=0
        for dev in self.devices:
            if dev[0]==1:
                counter+=1
            if dev[0]==2:
                counter+=1
            if dev[0]==3:
                counter+=1
        if counter!=3:
            print "ERROR : One or more of the devices are missing"
        else:
            print "Succesful"

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
            print "Cannot send the command '" + command[:-1] + "' because the device is missing."
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

    def show_id(self,dev):
        #Show motor id
        motor_id=self.send_command(dev,"?\n",True)
        print "Motor id is: "+str(motor_id)

    def auto_speed_send(self,dev,status):
        #Send speed of the motor automatically with 62.5 Hz (0 or 1)
        self.send_command(dev,"gs"+str(status)+"\n")

    def auto_off(self,dev,status):
        #Motor turns itself off after 1.6 seconds after the last speed command.
        #It can be turned of: 0 or 1
        self.send_command(dev,"fs"+str(status)+"\n")

    #ROBOT MOVEMENTS

    #
    #Speed is in per cents of the maximum speed.
    #
    def speed_acceptable(self,speed):
        if speed>=0 and speed<=100:
            return True
        else:
            print "Not acceptable speed: "+str(speed)+". Should be between 0 and 100"
            return False
    
    def go_forward(self,speed):
        if speed_acceptable():
            speed = int(speed*1.9)
            self.go_pid(1,-speed)
            self.go_pid(2,speed)

    def go_backward(self,speed):
        if speed_acceptable():
            speed = int(speed*1.9)
            self.go_pid(1,speed)
            self.go_pid(2,-speed)

    def turn_left(self,speed):
        if speed_acceptable():
            speed = int(speed*1.9)
            self.go_pid(1,speed)
            self.go_pid(2,speed)
            self.go_pid(3,speed)

    def turn_right(self,speed):
        if speed_acceptable():
            speed = int(speed*1.9)
            self.go_pid(1,-speed)
            self.go_pid(2,-speed)
            self.go_pid(3,-speed)

    def go_left(self,speed):
        if speed_acceptable():
            speed = int(speed*1.9)
            self.go_pid(1,speed)
            self.go_pid(2,speed)
            self.go_pid(3,-int(0.71*speed))

    def go_right(self,speed):
        if speed_acceptable():
            speed = int(speed*1.9)
            self.go_pid(1,-speed)
            self.go_pid(2,-speed)
            self.go_pid(3,int(0.71*speed))
