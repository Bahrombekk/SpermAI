from ultralytics import YOLO
import cv2

class SpermDetector:
    def __init__(self, model_path):
        self.model = YOLO(model_path)
        self.classes = ['Live', 'Dead', 'Immature']
    
    def detect(self, image_path):
        image = cv2.imread(image_path)
        results = self.model(image)
        detections = []
        
        for box in results[0].boxes:
            class_id = int(box.cls)
            detections.append({
                'class_name': self.classes[class_id],
                'bbox': box.xyxy[0].tolist(),
                'confidence': box.conf.item()
            })
        
        return detections