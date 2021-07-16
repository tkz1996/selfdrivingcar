import RPi.GPIO as GPIO

#Initialize GPIO board
GPIO.setmode(GPIO.BCM) #Set GPIO naming to BOARD names (pin numbers and not the pin output type)
GPIO.setwarnings(False) #Disable warnings to make output terminal cleaner

#initialize pin variables
#Left right motor with respect to front of car (front of car at 2 forward drive wheels)
leftMotorControlOnePin = 17
leftMotorControlTwoPin = 27
leftMotorPWMPin = 22
rightMotorControlThreePin = 23
rightMotorControlFourPin = 24
rightMotorPWMPin = 25

#Setup required pins
GPIO.setup(leftMotorControlOnePin, GPIO.OUT)
GPIO.setup(leftMotorControlTwoPin, GPIO.OUT)
GPIO.setup(leftMotorPWMPin, GPIO.OUT)

GPIO.setup(rightMotorControlThreePin, GPIO.OUT)
GPIO.setup(rightMotorControlFourPin, GPIO.OUT)
GPIO.setup(rightMotorPWMPin, GPIO.OUT)

class Steer:
    def __init__(self, leftOne, leftTwo, leftPWM, rightThree, rightFour, rightPWM):
        
        self.angle = 0
        
        self.leftControlOne = leftOne
        self.leftControlTwo = leftTwo
        self.rightControlThree = rightThree
        self.rightControlFour = rightFour

        #initialize wheels duty cycle
        self.leftDC = 0
        self.rightDC = 0
        
        #NOTE: Use PWM output to control speed. Based on UNO, PWM default MAX FREQ set to 1000Hz
        # for stepper motor, increase in freq reduce jerking, reduce in freq reduces motor noise.
        GPIO.output(leftPWM, GPIO.LOW)
        self.leftMotorPWM = GPIO.PWM(leftPWM, 1500)
        self.leftMotorPWM.start(0) # Argument passed (0) is the duty cycle in terms of %
        GPIO.output(rightPWM, GPIO.LOW)
        self.rightMotorPWM = GPIO.PWM(rightPWM, 1500)
        self.rightMotorPWM.start(0) # Argument passed (0) is the duty cycle in terms of %
        self.maxDutyCycle = 50 # Set maximum speed limit for wheels, 45 for right turns, 50 for left
        self.minDutyCycle = 20 # Set minimum speed limit for wheels, default 20
        self.maxTurningAngle = 90 # Default 90
    
    def steering(self, angle):
        if angle > self.maxTurningAngle:
            angle = self.maxTurningAngle
        elif angle < -self.maxTurningAngle:
            angle = -self.maxTurningAngle
        self.angle = int(angle)
        newSpd = ((self.maxDutyCycle - self.minDutyCycle)/self.maxTurningAngle * abs(self.angle)) \
                  + self.minDutyCycle

        if self.angle < 0:
            self.rightDC = newSpd
            self.leftDC = self.minDutyCycle
        else:
            self.leftDC = newSpd
            self.rightDC = self.minDutyCycle

        self.leftMotorPWM.ChangeDutyCycle(self.leftDC)
        self.rightMotorPWM.ChangeDutyCycle(self.rightDC)
    
    def drive(self, direction = 1, initialDutyCycle = 0):

        #Starts car in forward drive by default
        #Left and Right GPIO Signals are OPPOSITE
        #E.g 1 high 4 high for backward, 2 high 3 high for forward
        if direction:
            GPIO.output(self.leftControlOne, GPIO.LOW)
            GPIO.output(self.leftControlTwo, GPIO.HIGH)
            GPIO.output(self.rightControlThree, GPIO.HIGH)
            GPIO.output(self.rightControlFour, GPIO.LOW)
        else:
            GPIO.output(self.leftControlOne, GPIO.HIGH)
            GPIO.output(self.leftControlTwo, GPIO.LOW)
            GPIO.output(self.rightControlThree, GPIO.LOW)
            GPIO.output(self.rightControlFour, GPIO.HIGH)
        
        self.leftMotorPWM.ChangeDutyCycle(initialDutyCycle)
        self.rightMotorPWM.ChangeDutyCycle(initialDutyCycle)
    
    def stop(self):
        self.leftMotorPWM.ChangeDutyCycle(0)
        self.rightMotorPWM.ChangeDutyCycle(0)
        GPIO.output(self.leftControlOne, GPIO.LOW)
        GPIO.output(self.leftControlTwo, GPIO.LOW)
        GPIO.output(self.rightControlThree, GPIO.LOW)
        GPIO.output(self.rightControlFour, GPIO.LOW)

    def terminate(self):
        GPIO.cleanup()

if __name__ == '__main__':
    import time
    driver = Steer(leftMotorControlOnePin, leftMotorControlTwoPin, leftMotorPWMPin,
             rightMotorControlThreePin, rightMotorControlFourPin, rightMotorPWMPin)
    driver.drive(initialDutyCycle = 40)
    time.sleep(5)
    driver.stop()
    driver.terminate()