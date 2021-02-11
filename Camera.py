import cv2
import numpy as np
import Direction as d


class Camera:
    def __init__(self, width = 640, height = 480, flip = False, ROI = 0.33, display = False, record = False):
        self.camera = cv2.VideoCapture(0)
        self.resolution = [height, width]
        # Set properties. Each returns === True on success (i.e. correct resolution)
        self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
        self.ROI = ROI
        self.grabbed, self.frame = None, None
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
        if self.flip:
            self.frame = cv2.flip(self.frame, -1)
    
    def close(self):
        self.camera.release()
        if self.record:
            self.video.release()
        return True

    def view(self, angle):
        print(f"Steering angle: {angle} degrees")
        if not angle:
            return

        x = int(self.resolution[1]//2 + np.tan(angle/180*np.pi)*(self.resolution[0]*self.ROI))
        cv2.line(self.frame,(self.resolution[1]//2,self.resolution[0]),(x,int(self.resolution[0]*(1 - self.ROI))), (0,0,255), 2)
        if self.display:
            cv2.imshow('Image', self.frame)
            cv2.waitKey(100)

        if self.record:
            self.video.write(self.frame)

    def lane_crop(self):
        h = self.resolution[0]
        self.cropped = self.frame[int(h*(1 - self.ROI)):h].copy()

    def lane_detection(self):
        self.cropped = cv2.GaussianBlur(self.cropped,(3,3), 1)
        self.cropped = cv2.cvtColor(self.cropped, cv2.COLOR_BGR2GRAY)
        retval, self.cropped = cv2.threshold(self.cropped, 150, 255, cv2.THRESH_BINARY+cv2.THRESH_OTSU)

        edges = cv2.Canny(self.cropped, 150, 255, apertureSize=5)
#         if self.display:
#             cv2.imshow('Edges', edges)
#             cv2.waitKey(0)
#             cv2.destroyAllWindows()

        lines = cv2.HoughLinesP(edges, 1, np.pi/180, 30, None, minLineLength=75, maxLineGap=50)
#         cv2.line(self.frame,(self.resolution[1]//2,self.resolution[0]),(self.resolution[1]//2,int(self.resolution[0]*(1 - self.ROI))), (0,0,255), 2)
#         cv2.line(self.frame,(10,10),(100,10), (255,0,0), 2)
#         cv2.putText(self.frame, "X", (120, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 0, 0), 2, cv2.LINE_AA)
#         cv2.line(self.frame,(10,10),(10,100), (0,0,255), 2)
#         cv2.putText(self.frame, "Y", (20, 120), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2, cv2.LINE_AA)

        if lines is not None and (self.display or self.record):
            for line in lines:
                x1,y1,x2,y2 = line[0]
                cv2.line(self.frame,(x1,y1+int(self.resolution[0]*(1-self.ROI))),(x2,y2+int(self.resolution[0]*(1-self.ROI))),(0,255,0),2)
        return lines


if __name__ == '__main__':
    cam = Camera(display = True, record = False)
    try:
        while True:
            cam.capture()
            cam.lane_crop()
            vectors = cam.lane_detection()
            if vectors is None:
                continue

            direction = d.get_direction(cam.ROI, cam.resolution, vectors)
            cam.view(direction)
    except KeyboardInterrupt:
        pass

    cv2.destroyAllWindows()
    cam.close()
    print("Ending script")
