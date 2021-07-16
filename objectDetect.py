import numpy as np
from tflite_runtime.interpreter import Interpreter
import re


class detector():
    def __init__(self, modelPath = 'objectdetect.tflite', \
                 classLabelPath = 'objectlabelmap.txt', \
                 threshold = 0.7):
        
        self.modelPath = modelPath
        self.classLabelPath = classLabelPath
        self.inputImg = None
        self.threshold = threshold
        
        self.labels = {}
        self.load_labels()

        self.interpreter = Interpreter(self.modelPath)
        self.interpreter.allocate_tensors()
    
    def load_labels(self):
        with open(self.classLabelPath, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            for row_number, content in enumerate(lines):
                pair = re.split(r'[:\s]+', content.strip(), maxsplit=1)
                if len(pair) == 2 and pair[0].strip().isdigit():
                    self.labels[int(pair[0])] = pair[1].strip()
                else:
                    self.labels[row_number] = pair[0].strip()
    
    def setTensors(self, Img):
        """ Input argument Img MUST BE RESIZED before passing into function."""
        self.inputImg = Img

        """Set input tensor as Img"""
        tensor_index = self.interpreter.get_input_details()[0]['index']
        input_tensor = self.interpreter.tensor(tensor_index)()[0]
        input_tensor[:, :] = self.inputImg
    
    def get_output_tensor(self, index):
        """Get output from tensor given an index"""
        output_details = self.interpreter.get_output_details()[index]
        tensor = np.squeeze(self.interpreter.get_tensor(output_details['index']))
        return tensor

    def detect_objects(self):
        """Returns a list of detection results, each a dictionary of object info."""
        self.interpreter.invoke()

        # Get all output details
        boxes = self.get_output_tensor(0)
        classes = self.get_output_tensor(1)
        scores = self.get_output_tensor(2)
        count = int(self.get_output_tensor(3))

        results = []
        items = (0,1,2,3,5,6,7,9,10,11)
        for i in range(count):
            if scores[i] >= self.threshold and int(classes[i]) in items:
                result = {'bounding_box': boxes[i], \
                          'class_id': int(classes[i]), \
                          'score': scores[i] \
                          }
                results.append(result)
        return results

