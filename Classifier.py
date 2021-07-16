import numpy as np
from tflite_runtime.interpreter import Interpreter
from cv2 import cvtColor, COLOR_RGB2GRAY

class interpreter():
    def __init__(self, modelPath = 'laneDirectionModel_Lite.tflite', \
                 classLabelPath = 'classiferAngle.txt'):
        
        self.modelPath = modelPath
        self.classLabelPath = classLabelPath
        self.inputImg = None
        
        self.labels = {}
        self.load_labels()

        self.interpreter = Interpreter(self.modelPath)
        self.interpreter.allocate_tensors()


    def load_labels(self):
        with open(self.classLabelPath, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            for row_number, content in enumerate(lines):
                self.labels[row_number] = int(content)


    def setTensors(self, Img):

        self.inputImg = cvtColor(Img, COLOR_RGB2GRAY)
        self.inputImg = self.inputImg.astype(np.float32)
        self.inputImg = np.expand_dims(self.inputImg, 0)
        self.inputImg = np.expand_dims(self.inputImg, -1)
        
        input_details = self.interpreter.get_input_details()
        input_shape = input_details[0]['shape']
        self.interpreter.set_tensor(input_details[0]['index'], self.inputImg)


    def predict(self):
        
        self.interpreter.invoke()
        outputDetails = self.interpreter.get_output_details()[0]
        output = np.squeeze(self.interpreter.get_tensor(outputDetails['index']))
        ordered = np.argpartition(-output, 1)

#         scale, zeroPoint = outputDetails['quantization']
#         output = scale * (output - zeroPoint)
        predictedClass, probability = ordered[0], output[ordered[0]]

        #Equation to convert class label to angle
        return int(self.labels[predictedClass])


if __name__ == '__main__':
    from cv2 import imread
    import time
    
    classifier = interpreter()
    
    startTime = time.time()
    image = imread("test.jpg")
    
    classifier.setTensors(image)
    direction = classifier.predict()
    print(direction)
    print(f'Time Taken: {time.time()-startTime}s')
