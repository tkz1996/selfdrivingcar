import cv2
import numpy as np


class Camera:
    def __init__(self, width = 640, height = 480, flip = False, ROI = 0.2, \
                 display = False, record = False, cvMode = True, createData = False, \
                 dataHeight = 100, dataWidth = 600):
        self.camera = cv2.VideoCapture(0)
        self.resolution = [height, width]
        # Set properties. Each returns === True on success (i.e. correct resolution)
        self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
        
        self.cvMode = cvMode
        self.ROI = ROI
        self.grabbed, self.frame = None, None
        self.edges = None # Array containing edge map

        self.dataResolution = (dataHeight, dataWidth) # Resolution of training image
        self.createData = createData # Boolean to check if need to create data for ML
        self.classifierData = None # Attribute to store classifier image data

        self.flip = flip
        self.cropped = None
        self.display = display
        self.record = record
        if record:
            self.video = cv2.VideoWriter('CarVision.avi',  
                         cv2.VideoWriter_fourcc(*'MJPG'), 
                         10, (width,height))
    
    def capture(self):
        self.grabbed, self.frame = self.camera.read()
        if not self.grabbed:
            raise Exception("Failed to capture from camera")
        if self.flip:
            self.frame = cv2.flip(self.frame, -1)
    
    def close(self):
        self.camera.release()
        if self.record:
            self.video.release()
        return True

    #Draws finalized direction line onto image frame
    def draw(self, angle, createData = False):
        if angle != None:

            x = int(self.resolution[1]//2 + np.tan(angle/180*np.pi)*(self.resolution[0]*self.ROI))
            cv2.line(self.frame,(self.resolution[1]//2,self.resolution[0]),(x,int(self.resolution[0]*(1 - self.ROI))),
                     (0,0,255), 2)
            cv2.putText(self.frame, f"{angle} deg", (x+10,int(self.resolution[0]*(1 - self.ROI))),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255), 1, cv2.LINE_AA)

        return angle
    def view(self, leftSpd = None, rightSpd = None, fps = None):
        if leftSpd:
            cv2.putText(self.frame, f"L:{round(leftSpd,1)}%", (10,20),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0,0,255), 1, cv2.LINE_AA)
        if rightSpd:
            cv2.putText(self.frame, f"R:{round(rightSpd,1)}%", (self.resolution[1]-75,20),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0,0,255), 1, cv2.LINE_AA)
        if fps:
            cv2.putText(self.frame, f"{round(fps)}fps", (self.resolution[1]-75,self.resolution[0]-10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0,0,255), 1, cv2.LINE_AA)
        if self.record:
            self.video.write(self.frame)

        if self.display:
            cv2.imshow('Image', self.frame)
            cv2.waitKey(1)

    def lane_crop(self):
        r = self.resolution
        if self.createData or (not self.cvMode):
            self.classifierData = self.frame[r[0]-self.dataResolution[0]:, r[1]//2-self.dataResolution[1]//2 : r[1]//2+self.dataResolution[1]//2].copy()
        if self.cvMode:
            self.cropped = self.frame[int(r[0]*(1 - self.ROI)):r[0]].copy()

    def lane_edges(self):
        self.cropped = cv2.cvtColor(self.cropped, cv2.COLOR_BGR2GRAY)
        
        #Canny Edge Method
#         self.cropped = cv2.GaussianBlur(self.cropped,(5,5), 1, 1, cv2.BORDER_DEFAULT)
#         retval, self.cropped = cv2.threshold(self.cropped, 110, 255, cv2.THRESH_BINARY)

        #Modified Canny Edge method
        self.cropped = cv2.inRange(self.cropped, 0, 70)

        self.edges = cv2.Canny(self.cropped, 175, 225, apertureSize=3)

    def lane_detection(self):

        lines = cv2.HoughLinesP(self.edges, 1, np.pi/180, 50, minLineLength=50, maxLineGap=30)
#         cv2.line(self.frame,(self.resolution[1]//2,self.resolution[0]),(self.resolution[1]//2,int(self.resolution[0]*(1 - self.ROI))), (0,0,255), 2)
#         cv2.line(self.frame,(10,10),(100,10), (255,0,0), 2)
#         cv2.putText(self.frame, "X", (120, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 0, 0), 2, cv2.LINE_AA)
#         cv2.line(self.frame,(10,10),(10,100), (0,0,255), 2)
#         cv2.putText(self.frame, "Y", (20, 120), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2, cv2.LINE_AA)

        if lines is not None and (self.display or self.record):
            retLines = list()
            for line in lines:
                x1,y1,x2,y2 = line[0]
                y = y2 - y1
                if abs(y) < 20: #Reject lines that are too horizontal
                    continue
                if (x1 < self.resolution[1]//40 and x2 < self.resolution[1]//40) or \
                   (x1 > (39*self.resolution[1]//40) and x2 > (39*self.resolution[1]//40)):
                    #Reject lines that are at the side of the image (border lines)
                    continue
                retLines.append(line)
                cv2.line(self.frame,(x1,y1+int(self.resolution[0]*(1-self.ROI))),\
                         (x2,y2+int(self.resolution[0]*(1-self.ROI))),(0,255,0),2)
            lines = retLines

        return lines
    
    def create_data(self, angle, fileName, imgType = 'jpg'):
        from os import getcwd, path
        writeLocation = path.join(getcwd(),'dataset','train')
        
        # Algorithm to split data into classes
        stepSize = 15
        maxAngle = 60
        maxClasses = (maxAngle*2)//stepSize
        classLabel = angle//stepSize + (maxAngle//stepSize)
        if classLabel < 0:
            classLabel = 0
        if classLabel > maxClasses:
            classLabel = maxClasses

        fileName = str(fileName) + '.' + imgType
        fileLocation = path.join(writeLocation, str(int(classLabel)), fileName)
        return cv2.imwrite(fileLocation, self.classifierData)

    def draw_objects(self, results, labels):
        for obj in results:
            # Convert the bounding box figures from relative coordinates
            # to absolute coordinates based on the original resolution
            ymin, xmin, ymax, xmax = obj['bounding_box']
            xmin = int(xmin * self.resolution[1])
            xmax = int(xmax * self.resolution[1])
            ymin = int(ymin * self.resolution[0])
            ymax = int(ymax * self.resolution[0])

            # Overlay the box, label, and score on the camera preview
            self.frame = cv2.rectangle(self.frame, (xmin, ymin), (xmax,ymax), (0, 255, 0), 2)
            self.frame = cv2.putText(self.frame, \
                                     '%s:%.2f' % (labels[obj['class_id']], obj['score']), \
                                     (xmin, ymin-5), cv2.FONT_HERSHEY_SIMPLEX, \
                                     0.5, (0,255,0), 1, cv2.LINE_AA)

if __name__ == '__main__':
    import Direction as d
    import time

    cam = Camera(display = True, record = False, flip = True,\
                 cvMode = False, createData = False)
    is_objectDetect = False

    if not cam.cvMode:
        import Classifier
        classifier = Classifier.interpreter()
    
    if is_objectDetect:
        import objectDetect
        detector = objectDetect.detector()

    try:
        counter = 0
        while True:
            counter += 1
            cam.capture()

            # Detect if objects in the way.
            if is_objectDetect:
                startTime = time.time()
                detector.setTensors(cv2.resize(cam.frame, dsize=(300, 300)))
                results = detector.detect_objects()
                print(f'Time elasped: {time.time() - startTime}s')
                if len(results) > 0:
                    cam.draw_objects(results, detector.labels)
                    cam.view()
                    continue

            cam.lane_crop()

            if cam.cvMode:
                cam.lane_edges()
                vectors = cam.lane_detection()
                direction = d.get_direction(cam.ROI, cam.resolution, vectors)

            else:
                classifier.setTensors(cam.classifierData)
                direction = classifier.predict()
                print(direction)
                
            if direction != None and cam.createData and counter % 2 == 1:
                cam.create_data(angle = direction, fileName = counter)

            cam.draw(direction)
            cam.view()
    except KeyboardInterrupt:
        pass

    cv2.destroyAllWindows()
    cam.close()
    print("Ending script")