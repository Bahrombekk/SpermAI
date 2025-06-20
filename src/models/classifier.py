from ultralytics import YOLO
import cv2
import numpy as np

class SpermClassifier:
    def __init__(self, model_path):
        self.model = YOLO(model_path)
        self.classes = ['Normal', 'Abnormal', 'Other']
    
    def classify(self, image):
        # Resize image to 224x224
        image_resized = cv2.resize(image, (224, 224))
        results = self.model(image_resized)
        class_id = int(results[0].probs.top1)
        return {
            'class_name': self.classes[class_id],
            'confidence': results[0].probs.top1conf.item()
        }