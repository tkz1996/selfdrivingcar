from Camera import *
from MotorDriver import *
from PD import *
import time

driver = Steer(leftMotorControlOnePin, leftMotorControlTwoPin, leftMotorPWMPin,
             rightMotorControlThreePin, rightMotorControlFourPin, rightMotorPWMPin)
cam = Camera(display = False, record = True, flip = True, cvMode = True, createData = False)

# Set object detection mode
is_objectDetect = True
if is_objectDetect:
    import objectDetect
    detector = objectDetect.detector(threshold = 0.5)

# Imports modules according to mode
if cam.cvMode:
    from Direction import *
else:
    import Classifier
    classifier = Classifier.interpreter()

driver.drive()
controller = PD()
offRoadCounter = 0
clockCounter = 0

try:
    time.sleep(2)
    startTime = time.time()
    while True:
        clockCounter += 1
        cam.capture()

        if is_objectDetect and clockCounter % 20 == 0:

            detector.setTensors(cv2.resize(cam.frame, dsize=(300, 300)))
            results = detector.detect_objects()
            if len(results) > 0:
                driver.stop()
                print("Obstacle detected.")
                cam.draw_objects(results, detector.labels)
                cam.view(driver.leftDC, driver.rightDC)
                continue

        cam.lane_crop()

        if cam.cvMode:
            cam.lane_edges()
            vectors = cam.lane_detection()
            direction = get_direction(cam.ROI, cam.resolution, vectors)
        else:
            classifier.setTensors(cam.classifierData)
            direction = classifier.predict()

        direction = cam.draw(direction)

        if direction != None:
            if cam.createData:
                cam.create_data(angle = direction, fileName = clockCounter)
            offRoadCounter -= 1
            steeringAngle = controller.control(direction)
            driver.steering(steeringAngle)
        else:
            offRoadCounter += 1
            if offRoadCounter > 9:
                print("Car off lane")
                break

        cam.view(driver.leftDC, driver.rightDC)

except KeyboardInterrupt:
    pass

print(f'Average Cycle Runtime: {(time.time()-startTime)/clockCounter}s')
driver.stop()
driver.terminate()
cv2.destroyAllWindows()
cam.close()
print("Ending script")