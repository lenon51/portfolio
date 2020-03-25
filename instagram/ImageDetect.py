import cv2
import numpy as np

class ImageDetect():
    def __init__(self):
        self.path_config = r'C:\Temp\Schedule'
        self.image_config = self.path_config + r'\weights\yolov3.cfg'
        self.image_weights = self.path_config + r'\weights\yolov3.weights'
        self.image_class = self.path_config + r'\weights\coco.names'
        
        # read pre-trained model and config file
        self.net = cv2.dnn.readNet(self.image_weights, self.image_config)
        
        self.classes = None
        with open(self.image_class, 'r') as f:
            self.classes = [line.strip() for line in f.readlines()]
        
    def read_image(self, image_arg):
        # read input image
        image = cv2.imread(image_arg)

        width = image.shape[1]
        height = image.shape[0]
        scale = 0.00392

        # create input blob 
        blob = cv2.dnn.blobFromImage(image, scale, (416,416), (0,0,0), True, crop=False)

        # set input blob for the network
        self.net.setInput(blob)        
        
        return self.get_detect_class(width, height, image)
    
    def get_detect_class(self, Width, Height, image):
        # run inference through the network
        # and gather predictions from output layers
        outs = self.net.forward(self.get_output_layers())

        # initialization
        class_ids = []
        boxes = []
        confidences = []
        conf_threshold = 0.5
        nms_threshold = 0.4

        # for each detetion from each output layer 
        # get the confidence, class id, bounding box params
        # and ignore weak detections (confidence < 0.5)
        for out in outs:
            for detection in out:
                scores = detection[5:]
                class_id = np.argmax(scores)
                confidence = scores[class_id]
                if confidence > 0.5:
                    center_x = int(detection[0] * Width)
                    center_y = int(detection[1] * Height)
                    w = int(detection[2] * Width)
                    h = int(detection[3] * Height)
                    x = center_x - w / 2
                    y = center_y - h / 2
                    class_ids.append(class_id)
                    confidences.append(float(confidence))
                    boxes.append([x, y, w, h])

        # apply non-max suppression
        indices = cv2.dnn.NMSBoxes(boxes, confidences, conf_threshold, nms_threshold)

        # generate different colors for different classes 
        COLORS = np.random.uniform(0, 255, size=(len(self.classes), 3))        

        # go through the detections remaining
        # after nms and draw bounding box
        image_area = round(Width) * round(Height)
        lst_person = {}
        for i in indices:
            i = i[0]
            box = boxes[i]
            x = box[0]
            y = box[1]
            w = box[2]
            h = box[3]
            item = str(self.classes[class_ids[i]])
            
            if lst_person.get(item) == None:
                lst_person[item] = 0
            lst_person[item] += round(w) * round(h)

        if lst_person.get('person') != None:
            if lst_person['person'] / image_area > 0.5:
                return False
        return True
        
    def get_output_layers(self):
        layer_names = self.net.getLayerNames()    
        output_layers = [layer_names[i[0] - 1] for i in self.net.getUnconnectedOutLayers()]
        return output_layers        