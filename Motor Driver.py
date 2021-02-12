import RPi.GPIO as GPIO
import time

#Initialize GPIO board
GPIO.setmode(GPIO.BCM) #Set GPIO naming to BOARD names (pin numbers and not the pin output type)
GPIO.setwarnings(False) #Disable warnings to make output terminal cleaner

#initialize pin variables
leftMotorControlOnePin = 17
leftMotorControlTwoPin = 27
leftMotorPWMPin = 18
# rightMotorControlThreePin = 
# rightMotorControlFourPin = 
# rightMotorPWMPin = 

#Setup required pins
GPIO.setup(leftMotorControlOnePin, GPIO.OUT)
GPIO.setup(leftMotorControlTwoPin, GPIO.OUT)
GPIO.setup(leftMotorPWMPin, GPIO.OUT)

# GPIO.setup(rightMotorControlThreePin, GPIO.OUT)
# GPIO.setup(rightMotorControlFourPin, GPIO.OUT)
# GPIO.setup(rightMotorPWMPin, GPIO.OUT)

class Steer:
    def __init__(self, leftOne, leftTwo, leftPWM, rightThree, rightFour, rightPWM):
        
        self.angle = 0
        
        self.leftControlOne = leftOne
        self.leftControlTwo = leftTwo
        
        #NOTE: Use PWM output to control speed. Based on UNO, PWM default MAX FREQ set to 490Hz
        GPIO.output(leftPWM, GPIO.LOW)
        self.leftMotorPWM = GPIO.PWM(leftPWM, 490)
        self.leftMotorPWM.start(0) #Argument passed (0) is the duty cycle in terms of %
        
        self.leftspeed = 0
    
    def change_speed(self, angle):
        self.angle = angle
        return
    
    def drive(self, direction = 1):
        
        self.leftMotorPWM.ChangeDutyCycle(50)
        
        #Starts car in forward drive by default
        if direction:
            GPIO.output(self.leftControlOne, GPIO.HIGH)
            GPIO.output(self.leftControlTwo, GPIO.LOW)
        else:
            GPIO.output(self.leftControlOne, GPIO.LOW)
            GPIO.output(self.leftControlTwo, GPIO.HIGH)
            
        switch = False
        while True:
            if switch:
                self.leftMotorPWM.ChangeDutyCycle(30)
                switch = False
            else:
                self.leftMotorPWM.ChangeDutyCycle(90)
                switch = True
            time.sleep(1)
    
    def terminate(self):
        GPIO.cleanup()

temp = Steer(leftMotorControlOnePin, leftMotorControlTwoPin, leftMotorPWMPin,
             0, 0, 0)
temp.drive()